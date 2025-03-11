#!/bin/bash

# AppleのOCR機能を使った画像文字認識ツール起動スクリプト

# スクリプトのあるディレクトリに移動
cd "$(dirname "$0")"

# Anacondaの初期化とapple-ocr環境のアクティベーション 
echo "Anacondaを初期化しています..."

# 一般的なconda.shの場所を試す
CONDA_SH_FOUND=false
for CONDA_PATH in "$HOME/opt/anaconda3" "$HOME/anaconda3" "/opt/anaconda3" "/usr/local/anaconda3" "/opt/miniconda3" "$HOME/miniconda3"; do
    if [ -f "$CONDA_PATH/etc/profile.d/conda.sh" ]; then
        echo "conda.shを見つけました: $CONDA_PATH/etc/profile.d/conda.sh"
        source "$CONDA_PATH/etc/profile.d/conda.sh"
        CONDA_SH_FOUND=true
        break
    fi
done

if [ "$CONDA_SH_FOUND" = false ]; then
    echo "conda.shが見つかりません。別の方法を試みます..."
    # conda shell.bash hookを試す
    if command -v conda &> /dev/null; then
        echo "condaコマンドを見つけました。conda shell.bash hookを使用します..."
        eval "$(conda shell.bash hook)"
    else
        echo "condaコマンドが見つかりません。Anacondaが正しくインストールされているか確認してください。"
        exit 1
    fi
fi

# apple-ocr環境をアクティベート
echo "apple-ocr環境をアクティベートしています..."
conda activate apple-ocr || { 
    echo "apple-ocr環境のアクティベートに失敗しました。"
    echo "以下のコマンドを実行してから再試行してください："
    echo "conda init bash"
    exit 1
}

# 入力ディレクトリの確認
INPUT_DIR="input_images"
if [ ! -d "$INPUT_DIR" ]; then
    echo "入力ディレクトリ '$INPUT_DIR' が見つかりません。作成します..."
    mkdir -p "$INPUT_DIR"
    echo "画像ファイルを '$INPUT_DIR' ディレクトリに配置してから再実行してください。"
    exit 1
fi

# OCR処理を実行
echo "OCR処理を開始します..."
python main.py "$INPUT_DIR" --combine --move-processed --with-headers

# 処理結果の表示
if [ $? -eq 0 ]; then
    echo "OCR処理が完了しました。"
    echo "結果は '$INPUT_DIR/_output_texts' ディレクトリに保存されました。"
    echo "処理済みの画像は '$INPUT_DIR/_processed' ディレクトリに移動されました。"
else
    echo "OCR処理中にエラーが発生しました。"
fi

# 終了時に環境を戻す
conda deactivate
