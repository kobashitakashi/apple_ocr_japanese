# Apple OCR ツール

デジタルの中でも、やっぱり紙資料ありますよね。複数枚にわたる資料をスキャンしたあと「どうにか、OCRしてデジタル化したい…」そんなとき、複数画像からOCR化し、１つのテキストにまとめられます。

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

### シェルスクリプトを使用する場合

より簡単に使用するために、シェルスクリプトが用意されています：

```bash
./run_ocr.sh [オプション]
```

ヘルプを表示するには：

```bash
./run_ocr.sh --help
```

例：

```bash
./run_ocr.sh --detect-tables --level moderate
./run_ocr.sh -i ~/Desktop/screenshots --analyze-layout
```

### 出力先ディレクトリ

デフォルトでは、処理結果は入力ディレクトリ直下の**日時分秒のフォルダ**に保存されます。例えば：

```
input_images/
└── 20250311_140750/
    ├── _output_texts/  # テキストファイルの保存先
    └── _processed/     # 処理済み画像の移動先
```

別の場所に保存したい場合は、`--output_dir`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --output_dir 出力先ディレクトリ
```

例：

```bash
python main.py ~/Desktop/screenshots --output_dir ~/Desktop/extracted_text
```

この場合、日時分秒のフォルダは作成されず、指定したディレクトリに直接保存されます。

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

### 高度な機能

#### 表の検出と変換

画像内の表を検出し、Markdown形式の表に変換する機能を有効にするには、`--detect-tables`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --detect-tables
```

この機能は以下のような表を検出します：

- 区切り文字（タブ、パイプ、カンマなど）で区切られた表
- 等間隔のスペースで区切られた表
- 複数の列を持つ構造化されたテキスト

検出された表は、以下のようなMarkdown形式の表に変換されます：

```markdown
| 列1 | 列2 | 列3 |
| --- | --- | --- |
| データ1 | データ2 | データ3 |
| データ4 | データ5 | データ6 |
```

#### レイアウト解析

画像内のテキストレイアウトを解析し、適切なMarkdown形式に変換する機能を有効にするには、`--analyze-layout`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --analyze-layout
```

この機能は以下のようなレイアウト要素を検出します：

- インデントされたテキスト → Markdownの引用ブロック（`>`）に変換
- 段組みレイアウト → 適切な順序でテキストを再構成

#### 変換レベルの設定

表の検出やレイアウト解析の積極性を調整するには、`--conversion-level`オプションを使用します。

```bash
python main.py 画像ファイルが含まれるディレクトリ --detect-tables --conversion-level moderate
```

使用可能なレベル：

- `conservative`（デフォルト）: 確実な場合のみ変換（精度優先）
- `moderate`: バランスの取れた変換（精度と網羅性のバランス）
- `aggressive`: 可能性が高い場合も変換（網羅性優先）

例：

```bash
# 表の検出と変換を有効にし、積極的な変換レベルを設定
python main.py ~/Desktop/screenshots --detect-tables --conversion-level aggressive

# レイアウト解析を有効にし、バランスの取れた変換レベルを設定
python main.py ~/Desktop/screenshots --analyze-layout --conversion-level moderate

# 両方の機能を有効にする
python main.py ~/Desktop/screenshots --detect-tables --analyze-layout
```

## サポートされている画像形式

- PNG (.png)
- JPEG (.jpg, .jpeg)
- TIFF (.tiff)

## Markdown対応について

このツールは、OCR結果をMarkdown形式で保存します：

- 出力ファイルの拡張子は`.md`（Markdown）
- 各ファイルにはYAMLフロントマターが追加される（タイトル、日時、ソース情報）
- 統合ファイルには見出し（`# ファイル名`）とセパレータ（`---`）を追加可能

### 自動Markdown変換機能

このツールには、OCR結果を自動的にMarkdown形式に変換する機能が含まれています：

#### 見出しの自動検出

以下のパターンを見出しとして検出し、適切なMarkdown記法に変換します：

- 短い行（40文字未満）で、次の行が空行の場合 → `## テキスト`
- 数字+ドットで始まる行（例：「1. タイトル」） → `## 1. タイトル`
- 章や節を示すパターン（例：「第1章 タイトル」） → `# 第1章 タイトル`
- 特定の接頭辞（例：「はじめに」「概要」） → `## はじめに`

#### リストの自動検出

以下のパターンをリストとして検出し、Markdown記法に変換します：

- 箇条書き記号（「・」「-」「*」など）で始まる行 → `- テキスト`
- 数字+ドットで始まる行（番号付きリスト） → `1. テキスト`

#### テキスト強調の自動検出

以下のパターンをテキスト強調として検出し、Markdown記法に変換します：

- 「」で囲まれたテキスト → `**テキスト**`（太字）
- 『』で囲まれたテキスト → `*テキスト*`（斜体）
- 全角の「＊」や「＿」で囲まれたテキスト → 太字または斜体

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
- 表の検出とレイアウト解析は実験的な機能であり、すべての表やレイアウトを正確に検出できるわけではありません

## ライセンスと免責事項

### ライセンス

このプロジェクトはMITライセンスの下で公開されています。

簡潔に言えば：
- このソフトウェアは自由に使用、修正、配布することができます
- 商用利用も可能です
- 著作権表示とライセンス表示を保持してください
- 作者は一切の保証を提供しません

### 依存関係

このプロジェクトは以下のライブラリに依存しています：
- [PyObjC](https://github.com/ronaldoussoren/pyobjc)（MITライセンス）
  - pyobjc-core
  - pyobjc-framework-Vision
  - pyobjc-framework-Quartz

### 免責事項

- このツールはAppleのVisionフレームワークを使用しており、**macOSでのみ動作**します
- OCR処理の精度は画像の品質や内容に依存します
- このツールの使用によって生じたいかなる損害や問題に対しても、開発者は責任を負いません
- AppleのAPIやフレームワークの変更により、将来的に動作しなくなる可能性があります
- このツールはAppleの商標（Apple、Vision、macOSなど）を使用していますが、これらはAppleのAPIを使用していることを示すためだけに使用されています。このプロジェクトはAppleによって承認、スポンサー、または提携されているものではありません
