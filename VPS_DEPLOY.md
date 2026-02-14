# 🌐 VPSデプロイ手順書

YouTube字幕検索アプリをVPS上で公開する手順です。

---

## 0. 前提条件

| 項目 | 推奨 |
|------|------|
| OS | Ubuntu 22.04 / 24.04 LTS |
| スペック | 1 vCPU / 512MB RAM 以上 |
| サービス例 | ConoHa VPS, さくらのVPS, Vultr, DigitalOcean |

---

## 1. VPSの契約とSSH接続

### 1-1. VPSを契約する
お好みのVPSサービスでサーバーを契約します。OSは **Ubuntu** を選択してください。

### 1-2. SSH接続する
契約後に発行されるIPアドレスとパスワードを使って接続します。

```bash
# Macのターミナルから
ssh root@<VPSのIPアドレス>
```

初回は「接続して良いですか？」と聞かれるので `yes` を入力してEnter。
パスワードを入力すればサーバーに入れます。

---

## 2. セットアップ（コピペ一発）

SSH接続した状態で、以下のコマンドを **順番に** 実行してください。

### 2-1. コードをダウンロード＆セットアップ

```bash
# GitHubからクローン
git clone https://github.com/klight-ymd/youtube-keyword-search.git /tmp/yt-setup

# セットアップスクリプトを実行
cd /tmp/yt-setup
sudo bash setup.sh
```

これで自動的に以下が完了します：
- Python3のインストール
- 仮想環境の作成
- 依存パッケージのインストール
- ファイアウォールの設定（ポート8501を開放）
- systemdサービスの登録

---

## 3. cookies.txt の転送

YouTube字幕取得にはCookieが必要です。
ローカルPCからVPSへ `cookies.txt` を転送します。

### Macのターミナル（新しいタブ）で実行：

```bash
scp ~/antigravity/youtube-search/cookies.txt root@<VPSのIPアドレス>:/home/ytapp/youtube-search/cookies.txt
```

転送後、VPS側でファイルの所有者を変更：

```bash
# VPSのSSH接続側で実行
chown ytapp:ytapp /home/ytapp/youtube-search/cookies.txt
```

---

## 4. アプリの起動

```bash
sudo systemctl start youtube-search
```

### 動作確認

```bash
sudo systemctl status youtube-search
```

「active (running)」と表示されればOKです！

### ブラウザでアクセス

```
http://<VPSのIPアドレス>:8501
```

---

## 5. よく使うコマンド

| コマンド | 説明 |
|---------|------|
| `sudo systemctl start youtube-search` | アプリを起動 |
| `sudo systemctl stop youtube-search` | アプリを停止 |
| `sudo systemctl restart youtube-search` | アプリを再起動 |
| `sudo systemctl status youtube-search` | 状態を確認 |
| `sudo journalctl -u youtube-search -f` | ログをリアルタイム表示 |

---

## 6. コードの更新

アプリのコードを更新した場合：

```bash
# VPSで実行
cd /home/ytapp/youtube-search
sudo -u ytapp git pull
sudo systemctl restart youtube-search
```

---

## ⚠️ 注意事項

- `cookies.txt` は定期的に更新が必要です（2〜4週間程度で期限切れ）。
  期限が切れた場合は、再度ブラウザからエクスポートして転送してください。
- `cookies.txt` は **GitHubにアップロードしないでください**（`.gitignore` に設定済み）。
