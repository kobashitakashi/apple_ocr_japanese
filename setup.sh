#!/bin/bash

# Apple OCRツールのセットアップスクリプト
echo "Apple OCRツールのセットアップを開始します..."

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

# 環境チェック
echo "環境をチェックしています..."

# macOSであることを確認
if [[ "$(uname)" != "Darwin" ]]; then
    echo "エラー: このツールはmacOSでのみ動作します。"
    echo "現在のOS: $(uname)"
    exit 1
fi

echo "✓ macOSが検出されました。"

# Pythonのバージョンチェック
if ! command -v python3 &> /dev/null; then
    echo "エラー: python3が見つかりません。"
    echo "Python 3.6以上をインストールしてください。"
    echo "推奨: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $PYTHON_MAJOR -lt 3 || ($PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 6) ]]; then
    echo "エラー: Python 3.6以上が必要です。"
    echo "現在のバージョン: $PYTHON_VERSION"
    echo "Python 3.6以上をインストールしてください。"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION が検出されました。"

# 必要なディレクトリの作成
echo "必要なディレクトリを作成しています..."

if [ ! -d "input_images" ]; then
    mkdir -p input_images
    echo "✓ input_imagesディレクトリを作成しました。"
else
    echo "✓ input_imagesディレクトリは既に存在します。"
fi

# Python仮想環境のセットアップ
echo "Python仮想環境(.venv)をセットアップしています..."

if [ -d ".venv" ]; then
    echo "既存の.venv環境が見つかりました。再作成しますか？ [y/N]"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "既存の.venv環境を削除しています..."
        rm -rf .venv
    else
        echo "既存の.venv環境を使用します。"
    fi
fi

if [ ! -d ".venv" ]; then
    echo "Python仮想環境を作成しています..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "エラー: Python仮想環境の作成に失敗しました。"
        echo "python3-venvパッケージがインストールされているか確認してください。"
        exit 1
    fi
    echo "✓ Python仮想環境を作成しました。"
fi

# 仮想環境をアクティベート
echo "仮想環境をアクティベートしています..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "エラー: 仮想環境のアクティベートに失敗しました。"
    exit 1
fi

# 依存パッケージのインストール
echo "必要なパッケージをインストールしています..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "エラー: パッケージのインストールに失敗しました。"
    echo "requirements.txtを確認してください。"
    deactivate
    exit 1
fi

echo "✓ 必要なパッケージをインストールしました。"

# 実行権限の設定
echo "実行権限を設定しています..."
chmod +x run.sh
echo "✓ run.shに実行権限を付与しました。"

# 仮想環境を非アクティブ化
deactivate

echo ""
echo "セットアップが完了しました！"
echo ""
echo "使用方法:"
echo "1. 画像ファイルを input_images ディレクトリに配置します。"
echo "2. 以下のコマンドでOCRツールを実行します:"
echo "   ./run.sh"
echo ""
echo "オプションを確認するには:"
echo "   ./run.sh --help"
echo ""
echo "詳細はREADME.mdを参照してください。"
