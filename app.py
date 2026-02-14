
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import datetime
import pandas as pd
import time
import requests
import http.cookiejar
import os

# --- 関数定義 ---
def extract_video_id(url):
    """
    YouTubeのURLから動画IDを抽出する関数
    """
    if not url:
        return None
    try:
        parsed_url = urlparse(url)
        if parsed_url.hostname == 'youtu.be':
            return parsed_url.path[1:]
        if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
            if parsed_url.path == '/watch':
                p = parse_qs(parsed_url.query)
                return p['v'][0] if 'v' in p else None
            elif parsed_url.path.startswith('/embed/'):
                return parsed_url.path.split('/')[2]
            elif parsed_url.path.startswith('/v/'):
                return parsed_url.path.split('/')[2]
        return None
    except:
        return None

def format_timestamp(seconds):
    """秒数を HH:MM:SS 形式に変換する"""
    return str(datetime.timedelta(seconds=int(seconds)))

def fetch_video_title(session, video_id):
    """YouTubeのページからタイトルを取得する"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        response = session.get(url)
        if response.status_code == 200:
            html = response.text
            # <title>タイトル - YouTube</title> から抽出
            if "<title>" in html:
                start = html.find("<title>") + 7
                end = html.find("</title>")
                title = html[start:end].strip()
                # " - YouTube" を除去
                if title.endswith(" - YouTube"):
                    title = title[:-10].strip()
                return title
    except:
        pass
    return f"(タイトル取得失敗: {video_id})"

def search_transcript(transcript_data, keywords):
    """
    字幕データからキーワードを検索し、結果リストを返す
    （dict形式とdataclass形式の両方に対応）
    """
    results = []
    for entry in transcript_data:
        # dataclass（.text）とdict（['text']）の両方に対応
        text = entry.text if hasattr(entry, 'text') else entry['text']
        start_time = entry.start if hasattr(entry, 'start') else entry['start']
        
        # 複数キーワードのいずれかが含まれるか？ (OR検索)
        hit_keywords = []
        for k in keywords:
            if k.lower() in text.lower():
                hit_keywords.append(k)
        
        if hit_keywords:
            results.append({
                "seconds": start_time,
                "text": text,
                "keywords": hit_keywords
            })
    return results

def get_authenticated_api():
    """
    cookies.txtが存在する場合、読み込んで認証付きのAPIインスタンスを返す
    """
    session = requests.Session()
    # User-Agentを偽装（Bot判定回避のため重要）
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    cookie_file = 'cookies.txt'
    
    if os.path.exists(cookie_file):
        try:
            cookie_jar = http.cookiejar.MozillaCookieJar(cookie_file)
            cookie_jar.load(ignore_discard=True, ignore_expires=True)
            session.cookies = cookie_jar
            st.sidebar.success(f"✅ cookies.txt を読み込みました ({len(cookie_jar)} cookies loaded)")
            
            # デバッグ: 読み込んだCookieの内訳を表示
            cookie_preview = []
            for cookie in cookie_jar:
                if "youtube" in cookie.domain:
                    cookie_preview.append(f"{cookie.domain}: {cookie.name}")
            
            if cookie_preview:
                with st.sidebar.expander("読み込んだYouTube Cookie"):
                    st.sidebar.code("\n".join(cookie_preview))
            else:
                 st.sidebar.warning("⚠️ YouTube関連のCookieが見つかりません。")
        except Exception as e:
            st.sidebar.error(f"❌ cookies.txt の読み込み失敗: {e}")
            st.sidebar.warning("※ Netscape形式の cookies.txt である必要があります。")
            return YouTubeTranscriptApi() 
    else:
        st.sidebar.warning("⚠️ cookies.txt が見つかりません。")
        st.sidebar.caption("プロジェクトフォルダ直下に配置してください。")
            
    # http_clientとしてsessionを渡す
    return YouTubeTranscriptApi(http_client=session)

# --- ページ設定 ---
st.set_page_config(
    page_title="YouTube Keyword Search V2",
    page_icon="🔍",
    layout="wide"
)

# --- UI実装 ---
st.title("📺 YouTube字幕検索アプリ V2")
st.write("複数の動画から、複数のキーワードをまとめて検索できます。")

# サイドバー
with st.sidebar:
    st.header("使い方")
    st.markdown("""
    1. **動画URL**: 1行に1つずつ入力してください。
    2. **キーワード**: カンマ(,)またはスペースで区切って入力してください。
    3. **検索**: ボタンを押すと結果が表示されます。
    4. **保存**: 結果をCSVでダウンロードできます。
    """)
    st.info("※ 字幕がない動画や、無効なURLはスキップされます。")
    
    # Cookie情報の表示
    if os.path.exists('cookies.txt'):
         st.caption("ℹ️ Cookie認証モードで動作中")

# メイン入力エリア（2カラム）
col1, col2 = st.columns(2)

with col1:
    url_input_raw = st.text_area(
        "YouTube動画のURL（複数可・改行区切り）",
        value="https://www.youtube.com/watch?v=j9YpkSX7NNM",
        placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...",
        height=200
    )

with col2:
    keyword_input_raw = st.text_input(
        "検索キーワード（複数可・カンマ/スペース区切り）",
        value="Python, AI",
        placeholder="例: AI, Python, 機械学習"
    )

# 検索ボタン
if st.button("検索開始 🚀", type="primary", use_container_width=True):
    # 1. 入力データの整形
    urls = [line.strip() for line in url_input_raw.split('\n') if line.strip()]
    
    # キーワード分割（カンマをスペースに置換 -> split）
    keywords_raw = keyword_input_raw.replace('、', ' ').replace(',', ' ')
    keywords = [k.strip() for k in keywords_raw.split() if k.strip()]

    # 2. バリデーション
    if not urls:
        st.error("⚠️ YouTubeのURLを入力してください。")
    elif not keywords:
        st.error("⚠️ 検索キーワードを入力してください。")
    else:
        # 3. 検索処理実行
        results_data = [] # 最終的な表示用データ
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # APIインスタンス取得（Cookie対応）
        api_obj = get_authenticated_api()
        
        total_urls = len(urls)
        
        for i, url in enumerate(urls):
            current_progress = (i) / total_urls
            progress_bar.progress(current_progress)
            
            video_id = extract_video_id(url)
            
            if not video_id:
                st.toast(f"スキップ (無効なURL): {url}", icon="⏭️")
                continue
            
            status_text.text(f"検索中 ({i+1}/{total_urls}): {video_id}")
            
            try:
                # 字幕取得
                transcript_list = api_obj.list(video_id)
                try:
                     transcript = transcript_list.find_transcript(['ja', 'en', 'en-US'])
                except:
                     transcript = transcript_list.find_transcript(['ja', 'en']) 

                transcript_data = transcript.fetch()
                
                # タイトル取得（APIで使ったsessionを再利用）
                video_title = fetch_video_title(api_obj._fetcher._http_client, video_id)
                
                # 検索ロジック呼び出し
                found_entries = search_transcript(transcript_data, keywords)
                
                # 結果追加
                for res in found_entries:
                    start_time = res['seconds']
                    text = res['text']
                    hit_keywords = res['keywords']
                    
                    formatted_time = format_timestamp(start_time)
                    link_url = f"https://youtu.be/{video_id}?t={int(start_time)}"
                    
                    results_data.append({
                        "Title": video_title,
                        "Video ID": video_id,
                        "Original URL": url,
                        "Keyword": ", ".join(hit_keywords),
                        "Time": formatted_time,
                        "Text": text,
                        "Link": link_url,
                        "Seconds": start_time
                    })
                        
            except Exception as e:
                st.error(f"⚠️ エラー ({video_id}): 字幕を取得できませんでした。\n理由: {e}")
        
        # 完了処理
        progress_bar.progress(1.0)
        status_text.text("完了！")
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
        
        # 4. 結果表示
        if results_data:
            df = pd.DataFrame(results_data)
            
            st.success(f"🎉 検索完了: 合計 {len(df)} 件 ヒットしました！")
            
            tab1, tab2 = st.tabs(["📋 リスト表示", "📊 データテーブル"])
            
            with tab1:
                for index, row in df.iterrows():
                    with st.container():
                        st.markdown(f"**🎬 {row['Title']}**")
                        st.markdown(f"### {row['Time']} (Keyword: {row['Keyword']})")
                        st.markdown(f"[{row['Text']}]({row['Link']})")
                        st.divider()

            with tab2:
                st.dataframe(
                    df[['Title', 'Keyword', 'Time', 'Text', 'Link', 'Original URL']],
                    column_config={
                        "Title": st.column_config.TextColumn("タイトル"),
                        "Link": st.column_config.LinkColumn("再生リンク", display_text="再生 ▶️"),
                        "Original URL": st.column_config.LinkColumn("動画URL")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            
            csv_data = df.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 CSVをダウンロード",
                data=csv_data,
                file_name=f"youtube_search_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                type="primary"
            )
            
        else:
            st.warning("指定したキーワードは見つかりませんでした。")
