#!/bin/bash

# AppleのOCR機能を使った画像文字認識ツール起動スクリプト

# デフォルト設定
INPUT_DIR="input_images"
COMBINE=true
MOVE_PROCESSED=true
WITH_HEADERS=false
DETECT_TABLES=true
ANALYZE_LAYOUT=true
CONVERSION_LEVEL="moderate"
WORKERS=0  # 0はCPUコア数を自動検出
SHOW_HELP=false

# ヘルプメッセージ
function show_help {
    echo "使用方法: $0 [オプション]"
    echo ""
    echo "オプション:"
    echo "  -h, --help                 このヘルプメッセージを表示"
    echo "  -i, --input <ディレクトリ>    入力画像ディレクトリ（デフォルト: input_images）"
    echo "  --no-combine               統合ファイルを作成しない"
    echo "  --no-move                  処理済み画像を移動しない"
    echo "  --no-headers               統合ファイルにヘッダーを追加しない"
    echo "  --detect-tables            表の検出と変換を有効にする"
    echo "  --analyze-layout           レイアウト解析を有効にする"
    echo "  --level <レベル>            変換の積極性レベル（conservative, moderate, aggressive）"
    echo "  -w, --workers <数>          並列処理に使用するワーカー数（デフォルト: CPUコア数）"
    echo ""
    echo "例:"
    echo "  $0 --detect-tables --level moderate"
    echo "  $0 -i ~/Desktop/screenshots --analyze-layout"
    echo "  $0 --workers 4             # 4つのプロセスで並列処理"
    exit 0
}

# コマンドライン引数の解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        -i|--input)
            INPUT_DIR="$2"
            shift 2
            ;;
        --no-combine)
            COMBINE=false
            shift
            ;;
        --no-move)
            MOVE_PROCESSED=false
            shift
            ;;
        --no-headers)
            WITH_HEADERS=false
            shift
            ;;
        --detect-tables)
            DETECT_TABLES=true
            shift
            ;;
        --analyze-layout)
            ANALYZE_LAYOUT=true
            shift
            ;;
        --level)
            CONVERSION_LEVEL="$2"
            shift 2
            ;;
        -w|--workers)
            WORKERS="$2"
            shift 2
            ;;
        *)
            echo "エラー: 不明なオプション: $1"
            show_help
            ;;
    esac
done

# ヘルプの表示
if [ "$SHOW_HELP" = true ]; then
    show_help
fi

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
if [ ! -d "$INPUT_DIR" ]; then
    echo "入力ディレクトリ '$INPUT_DIR' が見つかりません。作成します..."
    mkdir -p "$INPUT_DIR"
    echo "画像ファイルを '$INPUT_DIR' ディレクトリに配置してから再実行してください。"
    exit 1
fi

# コマンドの構築
CMD="python main.py \"$INPUT_DIR\""

# オプションの追加
if [ "$COMBINE" = true ]; then
    CMD="$CMD --combine"
    
    if [ "$WITH_HEADERS" = true ]; then
        CMD="$CMD --with-headers"
    fi
fi

if [ "$MOVE_PROCESSED" = true ]; then
    CMD="$CMD --move-processed"
fi

if [ "$DETECT_TABLES" = true ]; then
    CMD="$CMD --detect-tables"
fi

if [ "$ANALYZE_LAYOUT" = true ]; then
    CMD="$CMD --analyze-layout"
fi

if [ "$CONVERSION_LEVEL" != "conservative" ]; then
    CMD="$CMD --conversion-level $CONVERSION_LEVEL"
fi

if [ "$WORKERS" -gt 0 ]; then
    CMD="$CMD --workers $WORKERS"
fi

# OCR処理を実行
echo "OCR処理を開始します..."
echo "実行コマンド: $CMD"
eval $CMD

# 処理結果の表示
if [ $? -eq 0 ]; then
    echo "OCR処理が完了しました。"
    echo "結果は日時分秒のフォルダに保存されました。"
    echo "フォルダ内に _output_texts と _processed ディレクトリが作成されています。"
else
    echo "OCR処理中にエラーが発生しました。"
fi

# 終了時に環境を戻す
conda deactivate
