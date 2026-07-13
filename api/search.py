"""
Vercel Serverless Function: YouTube字幕からキーワード検索

1リクエストにつき「1動画」を処理する設計。
（Vercelの関数実行時間制限に収めるため、複数動画はフロント側でループして呼び出す）

POST /api/search
  body: {"videoId": "xxxx", "keywords": ["Python", "AI"]}
  resp: {"videoId": "...", "title": "...", "results": [ ... ]}  200
        {"videoId": "...", "error": "..."}                      200 (処理は継続させたいので200で返す)
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import http.cookiejar
import datetime

import requests
from youtube_transcript_api import YouTubeTranscriptApi

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def resolve_proxy_url():
    """
    プロキシURLを環境変数から解決する（住宅用プロキシ推奨: クラウドIPブロック回避）。
    優先順位:
      1. WEBSHARE_PROXY_USERNAME / WEBSHARE_PROXY_PASSWORD  … Webshare住宅用
      2. PROXY_URL  … 任意のhttp(s)プロキシ (例: http://user:pass@host:port)
    設定がなければ None（=プロキシなし）。
    """
    ws_user = os.environ.get("WEBSHARE_PROXY_USERNAME")
    ws_pass = os.environ.get("WEBSHARE_PROXY_PASSWORD")
    if ws_user and ws_pass:
        host = os.environ.get("WEBSHARE_PROXY_HOST", "p.webshare.io")
        port = os.environ.get("WEBSHARE_PROXY_PORT", "80")
        # Webshareの住宅用ローテーションエンドポイント（毎リクエストでIPが変わる）
        return f"http://{ws_user}-rotate:{ws_pass}@{host}:{port}/"

    generic = os.environ.get("PROXY_URL")
    if generic:
        return generic.strip()

    return None


def build_session():
    """
    リクエスト用のセッションを構築する。
    - User-Agent を偽装（Bot判定回避）
    - YOUTUBE_COOKIES（Netscape形式のcookies.txtの中身）があれば読み込む
    - プロキシが設定されていれば適用（字幕取得・タイトル取得の両方に効く）
    """
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    cookies_env = os.environ.get("YOUTUBE_COOKIES")
    if cookies_env:
        cookie_path = "/tmp/cookies.txt"
        try:
            with open(cookie_path, "w", encoding="utf-8") as f:
                f.write(cookies_env)
            jar = http.cookiejar.MozillaCookieJar(cookie_path)
            jar.load(ignore_discard=True, ignore_expires=True)
            session.cookies = jar
        except Exception:
            # Cookieの読み込みに失敗しても、Cookieなしで続行する
            pass

    proxy_url = resolve_proxy_url()
    if proxy_url:
        session.proxies = {"http": proxy_url, "https": proxy_url}

    return session


def format_timestamp(seconds):
    """秒数を HH:MM:SS 形式に変換する"""
    return str(datetime.timedelta(seconds=int(seconds)))


def fetch_video_title(session, video_id):
    """YouTubeのページからタイトルを取得する"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = session.get(url, timeout=15)
        if response.status_code == 200:
            html = response.text
            if "<title>" in html:
                start = html.find("<title>") + 7
                end = html.find("</title>")
                title = html[start:end].strip()
                if title.endswith(" - YouTube"):
                    title = title[:-10].strip()
                return title
    except Exception:
        pass
    return f"(タイトル取得失敗: {video_id})"


def search_one(video_id, keywords):
    """1動画分の字幕を取得してキーワード検索した結果を返す"""
    session = build_session()
    api = YouTubeTranscriptApi(http_client=session)

    transcript_list = api.list(video_id)
    try:
        transcript = transcript_list.find_transcript(["ja", "en", "en-US"])
    except Exception:
        transcript = transcript_list.find_transcript(["ja", "en"])

    transcript_data = transcript.fetch()
    title = fetch_video_title(session, video_id)

    results = []
    for entry in transcript_data:
        text = entry.text if hasattr(entry, "text") else entry["text"]
        start_time = entry.start if hasattr(entry, "start") else entry["start"]

        hit_keywords = [k for k in keywords if k.lower() in text.lower()]
        if hit_keywords:
            results.append(
                {
                    "seconds": start_time,
                    "time": format_timestamp(start_time),
                    "text": text,
                    "keywords": hit_keywords,
                    "link": f"https://youtu.be/{video_id}?t={int(start_time)}",
                }
            )

    return title, results


class handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        payload = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw or b"{}")
        except Exception as e:
            self._send(400, {"error": f"invalid request body: {e}"})
            return

        video_id = (payload.get("videoId") or "").strip()
        keywords = [k for k in (payload.get("keywords") or []) if str(k).strip()]

        if not video_id:
            self._send(400, {"error": "videoId is required"})
            return
        if not keywords:
            self._send(400, {"error": "keywords is required"})
            return

        try:
            title, results = search_one(video_id, keywords)
            self._send(
                200,
                {"videoId": video_id, "title": title, "results": results},
            )
        except Exception as e:
            # 1動画が失敗しても全体を止めないよう、エラーも200で返す
            self._send(200, {"videoId": video_id, "error": str(e)})
