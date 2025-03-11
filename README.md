# Apple OCR ツール

AppleのVisionフレームワークを使用して、画像からテキストを抽出するPythonツールです。複数の画像ファイルをバッチ処理し、抽出されたテキストをMarkdownファイルに保存します。

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

### 出力先ディレクトリ

デフォルトでは、テキストファイルは入力ディレクトリ直下の`_output_texts`フォルダに保存されます。別の場所に保存したい場合は、`--output_dir`オプションを使用します。

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

デフォルトでは、統合ファイルの名前は現在の日時（例：`20250311_134940.md`）になります。別の名前を指定する場合は、`--combine_file`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --combine --combine_file まとめ.md
```

#### 統合ファイルのフォーマットオプション

デフォルトでは、統合ファイルにはテキストのみが含まれます。ファイル名のヘッダーやセパレータ（罫線）を追加したい場合は、以下のオプションを使用します。

- `--with-headers`: 各テキストの前にファイル名のヘッダー（`# ファイル名`）を追加
- `--with-separators`: 各テキストの後にセパレータ（罫線）を追加

```bash
python main.py ~/Desktop/screenshots --combine --with-headers --with-separators
```

注：統合モードでも、各画像ごとの個別テキストファイルは生成されます。

### 処理済み画像の移動

処理が完了した画像を入力ディレクトリ直下の`_processed`フォルダに移動したい場合は、`--move-processed`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --move-processed
```

これにより、処理済みの画像と未処理の画像を区別しやすくなります。

## サポートされている画像形式

- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tiff)

## Markdown対応について

このツールは、OCR結果をMarkdown形式で保存します：

- 出力ファイルの拡張子は`.md`（Markdown）
- 各ファイルにはYAMLフロントマターが追加される（タイトル、日時、ソース情報）
- 統合ファイルには見出し（`# ファイル名`）とセパレータ（`---`）を追加可能

### Markdownの利点

- 多くのテキストエディタやノートアプリで表示・編集可能
- 見出し、リスト、強調などの書式を簡単に追加可能
- HTMLやPDFなど他の形式への変換が容易
- バージョン管理システム（Git）との親和性が高い

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
