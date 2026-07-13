# ▲ Vercel デプロイ手順書

YouTube字幕検索アプリを **Vercel**（サーバーレス）で公開する手順です。
旧Streamlit版(`app.py`)から、静的フロント + Python API 関数に作り直したバージョンを使います。

---

## 構成

| ファイル | 役割 |
|---------|------|
| `index.html` | フロントエンド（入力フォーム・結果表示・CSV出力） |
| `api/search.py` | Python サーバーレス関数（1動画分の字幕検索） |
| `requirements.txt` | Vercel関数の依存（`youtube-transcript-api`, `requests`） |
| `vercel.json` | 関数の実行時間上限などの設定 |

> ⚠️ **重要な制約（必読）**
> Vercelは**データセンターIP**からYouTubeにアクセスするため、YouTubeにIPブロックされます。
> これは Cookie では回避できません（IPレベルのブロックのため）。**VPSやStreamlit Cloudでも同じ**です。
> クラウド上で安定動作させるには **住宅用プロキシ（residential proxy）** が実質必須です（§3.5 参照）。

---

## 1. 事前準備

- [Vercelアカウント](https://vercel.com/signup)（GitHubでログイン可）
- このリポジトリをGitHubにpush済みであること
- 手元に有効な `cookies.txt`（Netscape形式）

---

## 2. プロジェクトをVercelにインポート

### 方法A: ダッシュボード（おすすめ）
1. https://vercel.com/new を開く
2. このGitHubリポジトリを選択して **Import**
3. Framework Preset は **Other**（自動でOK）。Build設定はデフォルトのまま。
4. **Deploy** を押す

### 方法B: CLI
```bash
npm i -g vercel
vercel        # プレビューデプロイ
vercel --prod # 本番デプロイ
```

---

## 3. Cookie を環境変数に登録（重要）

`cookies.txt` はGitに含めない（`.gitignore`済み）ので、中身を環境変数で渡します。

### 3-1. cookies.txt の中身をコピー
```bash
cat ~/antigravity/youtube-search/cookies.txt | pbcopy   # Macならクリップボードにコピー
```

### 3-2. Vercelに登録
- ダッシュボード → 対象プロジェクト → **Settings → Environment Variables**
- 追加する:
  - **Name**: `YOUTUBE_COOKIES`
  - **Value**: `cookies.txt` の中身をそのまま貼り付け（複数行のまま）
  - **Environments**: Production / Preview / Development すべてにチェック
- **Save**

または CLI:
```bash
vercel env add YOUTUBE_COOKIES production
# プロンプトに cookies.txt の中身を貼り付け（末尾でEnter → Ctrl-D）
```

### 3-3. 再デプロイ
環境変数は次回デプロイから反映されます。ダッシュボードの **Redeploy**、または:
```bash
vercel --prod
```

---

## 3.5. 住宅用プロキシの設定（クラウドで動かすなら必須）

YouTubeはクラウドIPをブロックするため、住宅用プロキシ経由でアクセスします。
`youtube-transcript-api` が公式に推奨している **Webshare** の例を示します。

### 3.5-1. Webshareに登録
1. https://www.webshare.io/ でアカウント作成
2. **Residential**（住宅用）プロキシのプランを購入（従量課金・少額から可）
3. ダッシュボードの **Proxy → Proxy Settings** で **Proxy Username** と **Proxy Password** を控える

> ⚠️ 「Datacenter」ではなく必ず **Residential** を選んでください（Datacenterだとブロックされます）。

### 3.5-2. Vercelに環境変数を登録
ダッシュボード → **Settings → Environment Variables**、または CLI:
```bash
printf '%s' 'あなたのProxyユーザー名' | vercel env add WEBSHARE_PROXY_USERNAME production
printf '%s' 'あなたのProxyパスワード'   | vercel env add WEBSHARE_PROXY_PASSWORD production
# Preview / Development にも同様に登録すると、プレビュー環境でも動きます
```
登録後は再デプロイ（`vercel --prod`）で反映されます。

### 補足: Webshare以外のプロキシを使う場合
`WEBSHARE_*` の代わりに `PROXY_URL` を1つ設定すればOKです（http/https両方に適用）:
```
PROXY_URL = http://ユーザー名:パスワード@ホスト:ポート
```

### 対応している環境変数まとめ
| 変数名 | 用途 |
|--------|------|
| `YOUTUBE_COOKIES` | cookies.txt の中身（bot/同意判定回避） |
| `WEBSHARE_PROXY_USERNAME` / `WEBSHARE_PROXY_PASSWORD` | Webshare住宅用プロキシ |
| `WEBSHARE_PROXY_HOST` / `WEBSHARE_PROXY_PORT` | （任意）Webshareのエンドポイント上書き。既定 `p.webshare.io:80` |
| `PROXY_URL` | 任意のhttp(s)プロキシURL（Webshare未使用時） |

---

## 4. 動作確認

発行されたURL（例: `https://your-app.vercel.app`）にアクセスし、
URLとキーワードを入れて「検索開始」を押します。

- サイドの進捗バーが進み、ヒット行が表示されればOK
- 「取得できなかった動画」に `IP` や `bot` 系のエラーが出る場合 → §6 参照

---

## 5. Cookie の更新

`cookies.txt` は **2〜4週間で失効** します。字幕が取れなくなったら：
1. ブラウザ拡張などで新しい `cookies.txt` をエクスポート
2. §3-2 の手順で `YOUTUBE_COOKIES` を**上書き更新**
3. 再デプロイ

---

## 6. うまく動かないとき

| 症状 | 原因 / 対処 |
|------|------------|
| 全動画で字幕取得失敗（`YouTube is blocking requests from your IP` 等） | VercelのクラウドIPがブロックされている。**§3.5 の住宅用プロキシ**を設定してください。Cookieだけでは直りません（VPSでも同様）。 |
| 途中でタイムアウト | `vercel.json` の `maxDuration` を確認（Hobbyは最大60秒）。1動画=1リクエストに分割済みなので、字幕が非常に長い動画で発生しやすい。 |
| `YOUTUBE_COOKIES` が効かない | 環境変数保存後に**再デプロイ**したか確認。値がNetscape形式（`# HTTP Cookie File` から始まる複数行）か確認。 |

---

## 補足: ローカルで旧Streamlit版を動かす場合
```bash
pip install -r requirements-local.txt
streamlit run legacy/app.py
```
