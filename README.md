
# YouTube字幕検索アプリ V2 📺

YouTube動画の字幕を取得し、複数のキーワードが含まれる時間を横断検索できるアプリです。

## ✨ 主な機能 (V2)
- **複数動画検索**: 複数のYouTube URLを改行区切り入力して一括検索可能。
- **複数キーワード検索**: カンマまたはスペース区切りで複数のキーワードをOR検索可能。
- **CSVダウンロード**: 検索結果をExcelで開けるCSV形式（UTF-8 BOM付き）で保存可能。
- **インタラクティブな結果表示**: 検索結果を表形式・リスト形式で確認でき、再生位置へのリンクも自動生成。

## 🚀 使い方（ローカル実行）

### 1. 準備
ターミナルで以下のコマンドを実行し、必要なライブラリをインストールします。

```bash
pip install -r requirements.txt
```

### 2. アプリの起動
以下のコマンドでアプリを起動します。

```bash
streamlit run app.py
```

ブラウザが自動的に開き、アプリが表示されます。

---

## 🌐 インターネット公開（デプロイ）手順

このアプリをStreamlit Community Cloudで無料で公開する手順です。

### 1. GitHubにリポジトリを作成
1. GitHubにログインし、新しいリポジトリ（例: `youtube-keyword-search`）を作成します。
2. このフォルダの中身をGitHubにアップロードします。

```bash
# Gitの初期化（まだしていない場合）
git init
git add .
git commit -m "Initial commit with V2 features"

# リモートリポジトリの設定（GitHubで作成したリポジトリのURLを使用）
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```
**注意**: `YOUR_USERNAME` と `YOUR_REPO_NAME` はご自身のアカウント情報に置き換えてください。

### 2. Streamlit Community Cloudでデプロイ
1. [Streamlit Community Cloud](https://streamlit.io/cloud) にアクセスし、サインインします（GitHubアカウントでログインするとスムーズです）。
2. 右上の "New app" ボタンをクリックします。
3. "Use existing repo" を選択し、先ほど作成したGitHubリポジトリ（`YOUR_USERNAME/YOUR_REPO_NAME`）を選択します。
4. **Branch**: `main`
5. **Main file path**: `app.py`
6. "Deploy!" をクリックします。

数分待つと、アプリが公開され、URLが発行されます！
