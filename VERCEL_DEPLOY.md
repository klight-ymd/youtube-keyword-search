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

> ⚠️ **重要な制約**
> Vercelは**データセンターIP**からYouTubeにアクセスするため、Bot判定でブロックされやすいです。
> `cookies.txt` を環境変数に登録して認証しますが、それでも失敗する場合があります。
> これはプラットフォームの性質上の限界で、VPS（固定IP）より不利な点です。

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
| 全動画で字幕取得失敗（bot/IPブロック系エラー） | VercelのIPがブロックされている。Cookieを最新化しても直らない場合は、VPS版(`VPS_DEPLOY.md`)やStreamlit Community Cloud等の方が安定します。 |
| 途中でタイムアウト | `vercel.json` の `maxDuration` を確認（Hobbyは最大60秒）。1動画=1リクエストに分割済みなので、字幕が非常に長い動画で発生しやすい。 |
| `YOUTUBE_COOKIES` が効かない | 環境変数保存後に**再デプロイ**したか確認。値がNetscape形式（`# HTTP Cookie File` から始まる複数行）か確認。 |

---

## 補足: ローカルで旧Streamlit版を動かす場合
```bash
pip install -r requirements-local.txt
streamlit run app.py
```
