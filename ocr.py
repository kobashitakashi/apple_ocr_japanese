from Foundation import NSURL
from Vision import VNRecognizeTextRequest, VNImageRequestHandler, VNRequestTextRecognitionLevelAccurate
from Quartz import CIImage
import os
import re

def process_image(image_path, format_text=True):
    """
    画像ファイルからテキストを抽出する
    """
    print(f"OCR処理開始: {os.path.basename(image_path)}")
    
    # 画像の読み込み
    image_url = NSURL.fileURLWithPath_(image_path)
    image = CIImage.imageWithContentsOfURL_(image_url)
    
    if image is None:
        print(f"警告: 画像を読み込めませんでした: {image_path}")
        return "画像の読み込みに失敗しました。"
    
    # OCRリクエストの作成
    request = VNRecognizeTextRequest.alloc().init()
    request.setRecognitionLevel_(VNRequestTextRecognitionLevelAccurate)
    
    # 日本語を含む言語をサポート
    request.setRecognitionLanguages_(["ja", "en"])
    
    # OCR処理の実行
    handler = VNImageRequestHandler.alloc().initWithCIImage_options_(image, None)
    success = handler.performRequests_error_([request], None)
    
    if not success:
        print(f"警告: OCR処理に失敗しました: {image_path}")
        return "OCR処理に失敗しました。"
    
    # 結果の取得
    results = request.results()
    text = ""
    
    if results:
        for observation in results:
            candidates = observation.topCandidates_(1)
            if candidates and len(candidates) > 0:
                candidate = candidates[0]
                text += candidate.string() + "\n"
    else:
        print(f"警告: テキストが検出されませんでした: {image_path}")
        text = "テキストが検出されませんでした。"
    
    print(f"OCR処理完了: {os.path.basename(image_path)}")
    
    # テキストの後処理（改行の最適化）
    if format_text:
        formatted_text = format_ocr_text(text)
        # Markdown形式に変換
        return convert_to_markdown(formatted_text)
    else:
        return text

def format_ocr_text(text):
    """
    OCR結果のテキストを整形する
    - 不要な改行を削除
    - 段落を適切に再構成
    """
    if not text or text.isspace():
        return text
    
    # 段落を検出して処理
    paragraphs = []
    current_paragraph = []
    
    # 行ごとに処理
    lines = text.splitlines()
    for i, line in enumerate(lines):
        # 空行は段落の区切りとして扱う
        if not line or line.isspace():
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
            paragraphs.append('')  # 空行を保持
            continue
        
        # 行末が句読点で終わる場合は段落の終わりとして扱う
        if re.search(r'[。．.、，,!！?？]$', line):
            current_paragraph.append(line)
            paragraphs.append(' '.join(current_paragraph))
            current_paragraph = []
            continue
            
        # 次の行が存在し、現在の行が短い場合は改行を削除
        if i < len(lines) - 1 and len(line) < 160:  # 160文字未満を短い行とみなす
            current_paragraph.append(line)
        else:
            # 長い行または最後の行は段落として扱う
            current_paragraph.append(line)
            if current_paragraph:
                paragraphs.append(' '.join(current_paragraph))
                current_paragraph = []
    
    # 最後の段落を追加
    if current_paragraph:
        paragraphs.append(' '.join(current_paragraph))
    
    # 段落を改行で結合
    formatted_text = '\n\n'.join(paragraphs)
    
    # 連続する空行を1つにまとめる
    formatted_text = re.sub(r'\n{3,}', '\n\n', formatted_text)
    
    return formatted_text

def convert_to_markdown(text):
    """
    整形されたテキストをMarkdown形式に変換する
    - 見出しの検出
    - リストの検出
    - テキスト強調の検出
    """
    if not text:
        return text
    
    # 行ごとに処理
    lines = text.splitlines()
    markdown_lines = []
    
    # 前後の行のコンテキストを考慮して処理
    for i, line in enumerate(lines):
        # 空行はそのまま追加
        if not line or line.isspace():
            markdown_lines.append(line)
            continue
        
        # 見出しの検出
        heading_line = detect_heading(line, i, lines)
        if heading_line:
            markdown_lines.append(heading_line)
            continue
        
        # リストの検出
        list_line = detect_list(line)
        if list_line:
            markdown_lines.append(list_line)
            continue
        
        # テキスト強調の検出
        emphasized_line = detect_emphasis(line)
        markdown_lines.append(emphasized_line)
    
    return '\n'.join(markdown_lines)

def detect_heading(line, index, lines):
    """
    見出しを検出する
    """
    # 短い行（40文字未満）で、次の行が空行または存在しない場合は見出しの可能性が高い
    is_short = len(line.strip()) < 40
    is_followed_by_empty = (index == len(lines) - 1) or (not lines[index + 1].strip())
    
    # 数字+ドットで始まる行（例：「1. タイトル」）
    number_prefix_match = re.match(r'^(\d+[\.\)]) (.+)$', line.strip())
    
    # 章や節を示す可能性のある特定のパターン
    chapter_match = re.match(r'^(第\s*\d+\s*[章節]|[０-９]+[．\.]) (.+)$', line.strip())
    
    # 特定の接頭辞を持つ行
    prefix_match = re.match(r'^(はじめに|概要|序論|結論|まとめ|目次|付録|参考文献)[:：]?\s*(.+)?$', line.strip())
    
    if number_prefix_match and is_short:
        # 数字+ドットの見出し（例：「1. タイトル」→「## 1. タイトル」）
        prefix, content = number_prefix_match.groups()
        return f"## {prefix} {content}"
    elif chapter_match:
        # 章や節の見出し（例：「第1章 タイトル」→「# 第1章 タイトル」）
        prefix, content = chapter_match.groups()
        return f"# {prefix} {content}"
    elif prefix_match:
        # 特定の接頭辞を持つ見出し（例：「はじめに：内容」→「## はじめに：内容」）
        prefix, content = prefix_match.groups()
        if content:
            return f"## {prefix}：{content}"
        else:
            return f"## {prefix}"
    elif is_short and is_followed_by_empty:
        # 短い行で次が空行の場合は見出しとして扱う
        return f"## {line}"
    
    # 見出しでない場合は元の行を返す
    return line

def detect_list(line):
    """
    リストを検出する
    """
    # 箇条書き記号で始まる行
    bullet_match = re.match(r'^[\s　]*([・\-\*•◦‣⁃]) (.+)$', line.strip())
    
    # 数字+ドットで始まる行（番号付きリスト）
    number_match = re.match(r'^[\s　]*(\d+[\.\)]) (.+)$', line.strip())
    
    if bullet_match:
        # 箇条書きリスト（例：「・項目」→「- 項目」）
        _, content = bullet_match.groups()
        return f"- {content}"
    elif number_match:
        # 番号付きリスト（例：「1. 項目」→「1. 項目」）
        number, content = number_match.groups()
        return f"{number} {content}"
    
    # リストでない場合は元の行を返す
    return line

def detect_emphasis(line):
    """
    テキスト強調を検出する
    """
    # 「」や『』で囲まれたテキストを強調として検出
    line = re.sub(r'「([^」]+)」', r'**\1**', line)
    line = re.sub(r'『([^』]+)』', r'*\1*', line)
    
    # 全角の*や_で囲まれたテキストも強調として検出
    line = re.sub(r'＊([^＊]+)＊', r'**\1**', line)
    line = re.sub(r'＿([^＿]+)＿', r'*\1*', line)
    
    return line
