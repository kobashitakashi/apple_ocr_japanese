# Apple OCR ツール

AppleのVisionフレームワークを使用して、画像からテキストを抽出するPythonツールです。複数の画像ファイルをバッチ処理し、抽出されたテキストをテキストファイルに保存します。

## 前提条件

- macOS（AppleのVisionフレームワークを使用するため）
- Python 3.6以上
- Anaconda（仮想環境管理用）

## インストール

1. Anaconda環境を作成し、アクティベートします：

```bash
conda create -n apple-ocr python=3.9
conda activate apple-ocr
```

2. 必要なパッケージをインストールします：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本的な使い方

```bash
python main.py 画像ファイルが含まれるディレクトリ
```

例：

```bash
python main.py ~/Desktop/screenshots
```

### 出力先ディレクトリを指定する場合

```bash
python main.py 画像ファイルが含まれるディレクトリ --output_dir 出力先ディレクトリ
```

例：

```bash
python main.py ~/Desktop/screenshots --output_dir ~/Desktop/extracted_text
```

### テキスト整形機能を無効にする場合

デフォルトでは、OCR結果のテキストは自動的に整形され、不要な改行が削除されます。生のOCR結果をそのまま出力したい場合は、`--raw`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --raw
```

例：

```bash
python main.py ~/Desktop/screenshots --raw
```

### 複数画像のテキストを1つのファイルに統合する場合

複数の画像から抽出したテキストを1つのファイルにまとめたい場合は、`--combine`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --combine
```

統合ファイルの名前を指定する場合は、`--combine_file`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --combine --combine_file まとめ.txt
```

例：

```bash
python main.py ~/Desktop/screenshots --combine
python main.py ~/Desktop/screenshots --combine --combine_file document.txt
```

注：統合モードでも、各画像ごとの個別テキストファイルは生成されます。

## サポートされている画像形式

- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tiff)

## テキスト整形機能について

このツールには、OCR結果のテキストを自動的に整形する機能が含まれています：

- 不要な改行を削除し、文章の流れを維持
- 段落を適切に再構成
- 句読点で終わる行を段落の終わりとして扱う
- 空行は段落の区切りとして保持

これにより、スキャンした文書から抽出したテキストが読みやすくなります。

## 注意事項

- このツールはmacOSでのみ動作します（AppleのVisionフレームワークに依存しているため）
- 日本語と英語のテキスト認識に対応しています
- 画像の品質によって認識精度が変わる場合があります
- テキスト整形機能は完璧ではなく、文書の種類によっては手動での調整が必要な場合があります
