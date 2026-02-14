#!/bin/bash
# =============================================================================
# YouTube字幕検索アプリ - VPSセットアップスクリプト
# 対応OS: Ubuntu 22.04 / 24.04 LTS
# 使い方: sudo bash setup.sh
# =============================================================================

set -e

echo "=========================================="
echo " YouTube字幕検索アプリ セットアップ"
echo "=========================================="

# --- 1. システムパッケージの更新 ---
echo "[1/5] システムパッケージを更新中..."
apt update && apt upgrade -y

# --- 2. Python3とpipのインストール ---
echo "[2/5] Python3をインストール中..."
apt install -y python3 python3-pip python3-venv git

# --- 3. アプリ用ユーザーの作成（既存なら無視） ---
echo "[3/5] アプリ用ユーザーを作成中..."
if ! id "ytapp" &>/dev/null; then
    useradd -m -s /bin/bash ytapp
    echo "ユーザー 'ytapp' を作成しました。"
else
    echo "ユーザー 'ytapp' は既に存在します。"
fi

# --- 4. アプリのデプロイ ---
echo "[4/5] アプリをデプロイ中..."
APP_DIR="/home/ytapp/youtube-search"

if [ -d "$APP_DIR" ]; then
    echo "既存のディレクトリを更新します..."
    cd "$APP_DIR"
    sudo -u ytapp git pull
else
    echo "GitHubからクローン中..."
    sudo -u ytapp git clone https://github.com/klight-ymd/youtube-keyword-search.git "$APP_DIR"
    cd "$APP_DIR"
fi

# 仮想環境の作成
if [ ! -d "$APP_DIR/venv" ]; then
    sudo -u ytapp python3 -m venv "$APP_DIR/venv"
fi

# 依存パッケージのインストール
sudo -u ytapp "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

# Streamlit設定ディレクトリ
sudo -u ytapp mkdir -p /home/ytapp/.streamlit
cat > /home/ytapp/.streamlit/config.toml << 'EOF'
[server]
port = 8501
address = "0.0.0.0"
headless = true

[browser]
gatherUsageStats = false
EOF
chown ytapp:ytapp /home/ytapp/.streamlit/config.toml

# --- 5. ファイアウォール設定 ---
echo "[5/5] ファイアウォールを設定中..."
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp    # SSH
    ufw allow 8501/tcp  # Streamlit
    ufw --force enable
    echo "UFWでポート22と8501を開放しました。"
else
    echo "UFWが見つかりません。手動でポート8501を開放してください。"
fi

# --- 6. systemdサービスの登録 ---
echo "systemdサービスを登録中..."
cp "$APP_DIR/youtube-search.service" /etc/systemd/system/youtube-search.service
systemctl daemon-reload
systemctl enable youtube-search

echo ""
echo "=========================================="
echo " セットアップ完了！"
echo "=========================================="
echo ""
echo "▶ 次のステップ:"
echo "  1. cookies.txt を $APP_DIR/ にコピーしてください"
echo "  2. sudo systemctl start youtube-search でアプリを起動してください"
echo "  3. ブラウザで http://<このサーバーのIP>:8501 にアクセスしてください"
echo ""
