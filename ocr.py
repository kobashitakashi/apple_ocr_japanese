from Foundation import NSURL
from Vision import VNRecognizeTextRequest, VNImageRequestHandler, VNRequestTextRecognitionLevelAccurate
from Quartz import CIImage
import os
import re

def process_image(image_path, format_text=True, detect_tables=False, analyze_layout=False, conversion_level='conservative'):
    """
    画像ファイルからテキストを抽出する
    
    Parameters:
    -----------
    image_path : str
        画像ファイルのパス
    format_text : bool
        テキスト整形を行うかどうか
    detect_tables : bool
        表の検出と変換を行うかどうか
    analyze_layout : bool
        複雑なレイアウト解析を行うかどうか
    conversion_level : str
        変換の積極性レベル ('conservative', 'moderate', 'aggressive')
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
    
    # 位置情報を含むテキスト行のリスト（レイアウト解析用）
    text_lines_with_position = []
    
    if results:
        for observation in results:
            candidates = observation.topCandidates_(1)
            if candidates and len(candidates) > 0:
                candidate = candidates[0]
                text += candidate.string() + "\n"
                
                # レイアウト解析が有効な場合、位置情報を保存
                if analyze_layout:
                    # boundingBoxはNSRectで、左下原点の座標系
                    bounding_box = observation.boundingBox()
                    text_lines_with_position.append({
                        'text': candidate.string(),
                        'x': bounding_box.origin.x,
                        'y': bounding_box.origin.y,
                        'width': bounding_box.size.width,
                        'height': bounding_box.size.height
                    })
    else:
        print(f"警告: テキストが検出されませんでした: {image_path}")
        text = "テキストが検出されませんでした。"
    
    print(f"OCR処理完了: {os.path.basename(image_path)}")
    
    # テキストの後処理
    if format_text:
        # 基本的なテキスト整形
        formatted_text = format_ocr_text(text)
        
        # 表の検出と変換
        if detect_tables:
            formatted_text = detect_and_convert_tables(formatted_text, conversion_level)
        
        # 複雑なレイアウト解析
        if analyze_layout and text_lines_with_position:
            formatted_text = analyze_and_convert_layout(formatted_text, text_lines_with_position, conversion_level)
        
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
        if heading_line != line:  # 見出しとして検出された場合
            markdown_lines.append(heading_line)
            continue
        
        # リストの検出
        list_line = detect_list(line)
        if list_line != line:  # リストとして検出された場合
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

def detect_and_convert_tables(text, conversion_level='conservative'):
    """
    テキスト内の表を検出し、Markdown形式の表に変換する
    
    Parameters:
    -----------
    text : str
        変換対象のテキスト
    conversion_level : str
        変換の積極性レベル ('conservative', 'moderate', 'aggressive')
    
    Returns:
    --------
    str
        表が変換されたテキスト
    """
    if not text:
        return text
    
    # 行ごとに処理
    lines = text.splitlines()
    result_lines = []
    
    # 表の検出と変換
    i = 0
    while i < len(lines):
        # 表の候補となる連続した行を検出
        table_candidate_lines = detect_table_candidate(lines, i, conversion_level)
        
        if table_candidate_lines:
            # 表の候補が見つかった場合、Markdown形式の表に変換
            table_markdown = convert_to_markdown_table(table_candidate_lines, conversion_level)
            result_lines.append(table_markdown)
            i += len(table_candidate_lines)
        else:
            # 表の候補でない場合は、そのまま追加
            result_lines.append(lines[i])
            i += 1
    
    return '\n'.join(result_lines)

def detect_table_candidate(lines, start_index, conversion_level):
    """
    表の候補となる連続した行を検出する
    
    Parameters:
    -----------
    lines : list
        テキストの行のリスト
    start_index : int
        検出を開始する行のインデックス
    conversion_level : str
        変換の積極性レベル
    
    Returns:
    --------
    list or None
        表の候補となる行のリスト、または表でない場合はNone
    """
    if start_index >= len(lines):
        return None
    
    # 最小行数（ヘッダー行 + 区切り行 + データ行）
    min_table_rows = 3
    
    # 表の候補となる行の特徴
    # 1. 複数の列を持つ（区切り文字やスペースで区切られている）
    # 2. 各行の列数が一致または近い
    # 3. 各列の幅が一定または近い
    
    # 表の候補となる行を収集
    candidate_lines = []
    current_index = start_index
    
    # 最初の行が表のヘッダーの可能性があるか確認
    first_line = lines[current_index].strip()
    
    # 表の区切り文字を検出
    delimiters = ['\t', '|', ',']
    delimiter = None
    columns = None
    
    # 区切り文字で分割してみる
    for delim in delimiters:
        if delim in first_line:
            columns = first_line.split(delim)
            if len(columns) >= 2:  # 少なくとも2列以上
                delimiter = delim
                break
    
    # 区切り文字が見つからない場合、スペースで区切られた列を検出
    if not delimiter and conversion_level != 'conservative':
        # スペースが3つ以上連続している部分を区切りとみなす
        columns = re.split(r'\s{3,}', first_line)
        if len(columns) >= 2:
            delimiter = 'space'
    
    # 表の候補が見つからない場合
    if not delimiter or not columns or len(columns) < 2:
        return None
    
    # 列数
    column_count = len(columns)
    
    # 表の候補となる行を収集
    while current_index < len(lines) and len(candidate_lines) < 20:  # 最大20行まで
        line = lines[current_index].strip()
        
        # 空行または短すぎる行で表が終了
        if not line or len(line) < 3:
            break
        
        # 区切り文字で分割
        if delimiter == 'space':
            cols = re.split(r'\s{3,}', line)
        else:
            cols = line.split(delimiter)
        
        # 列数が大きく異なる場合は表の終了
        if len(cols) < column_count - 1 or len(cols) > column_count + 1:
            break
        
        candidate_lines.append(line)
        current_index += 1
    
    # 表の候補が最小行数未満の場合
    if len(candidate_lines) < min_table_rows and conversion_level == 'conservative':
        return None
    
    # 表の候補が最小行数未満でも、moderateまたはaggressiveモードでは2行以上あれば許容
    if len(candidate_lines) < 2 and conversion_level in ['moderate', 'aggressive']:
        return None
    
    return candidate_lines

def convert_to_markdown_table(table_lines, conversion_level):
    """
    表の候補となる行をMarkdown形式の表に変換する
    
    Parameters:
    -----------
    table_lines : list
        表の候補となる行のリスト
    conversion_level : str
        変換の積極性レベル
    
    Returns:
    --------
    str
        Markdown形式の表
    """
    if not table_lines:
        return ""
    
    # 表の区切り文字を検出
    delimiters = ['\t', '|', ',']
    delimiter = None
    
    # 最初の行で区切り文字を検出
    first_line = table_lines[0]
    for delim in delimiters:
        if delim in first_line:
            delimiter = delim
            break
    
    # 区切り文字が見つからない場合、スペースで区切られた列を検出
    if not delimiter:
        # スペースが3つ以上連続している部分を区切りとみなす
        delimiter = 'space'
    
    # 各行を列に分割
    table_data = []
    max_columns = 0
    
    for line in table_lines:
        if delimiter == 'space':
            columns = re.split(r'\s{3,}', line.strip())
        else:
            columns = [col.strip() for col in line.split(delimiter)]
        
        # 空の列を削除
        columns = [col for col in columns if col]
        
        if columns:
            table_data.append(columns)
            max_columns = max(max_columns, len(columns))
    
    # 表データが空の場合
    if not table_data or max_columns < 2:
        return '\n'.join(table_lines)
    
    # 各行の列数を揃える
    for i in range(len(table_data)):
        while len(table_data[i]) < max_columns:
            table_data[i].append('')
    
    # Markdown形式の表を生成
    markdown_table = []
    
    # ヘッダー行
    header = '| ' + ' | '.join(table_data[0]) + ' |'
    markdown_table.append(header)
    
    # 区切り行
    separator = '| ' + ' | '.join(['---'] * max_columns) + ' |'
    markdown_table.append(separator)
    
    # データ行
    for row in table_data[1:]:
        data_row = '| ' + ' | '.join(row) + ' |'
        markdown_table.append(data_row)
    
    return '\n'.join(markdown_table)

def analyze_and_convert_layout(text, text_lines_with_position, conversion_level='conservative'):
    """
    テキストのレイアウトを解析し、適切なMarkdown形式に変換する
    
    Parameters:
    -----------
    text : str
        変換対象のテキスト
    text_lines_with_position : list
        位置情報を含むテキスト行のリスト
    conversion_level : str
        変換の積極性レベル
    
    Returns:
    --------
    str
        レイアウトが変換されたテキスト
    """
    if not text or not text_lines_with_position:
        return text
    
    # 行ごとに処理
    lines = text.splitlines()
    result_lines = []
    
    # インデントレベルを検出して引用ブロックに変換
    result_lines = detect_and_convert_indentation(lines, text_lines_with_position, conversion_level)
    
    return '\n'.join(result_lines)

def detect_and_convert_indentation(lines, text_lines_with_position, conversion_level):
    """
    インデントレベルを検出して引用ブロックに変換する
    
    Parameters:
    -----------
    lines : list
        テキストの行のリスト
    text_lines_with_position : list
        位置情報を含むテキスト行のリスト
    conversion_level : str
        変換の積極性レベル
    
    Returns:
    --------
    list
        変換後の行のリスト
    """
    if not lines or not text_lines_with_position:
        return lines
    
    # X座標でソートして、最も左にある行を基準とする
    sorted_lines = sorted(text_lines_with_position, key=lambda x: x['x'])
    base_x = sorted_lines[0]['x']
    
    # インデントレベルのしきい値（ピクセル単位）
    indent_threshold = 20
    
    # 各行のインデントレベルを計算
    result_lines = []
    
    for i, line in enumerate(lines):
        if not line.strip():
            # 空行はそのまま追加
            result_lines.append(line)
            continue
        
        # 対応する位置情報を探す
        matching_line = None
        for pos_line in text_lines_with_position:
            if pos_line['text'] in line:
                matching_line = pos_line
                break
        
        if not matching_line:
            # 位置情報が見つからない場合はそのまま追加
            result_lines.append(line)
            continue
        
        # インデントレベルを計算
        indent_level = int((matching_line['x'] - base_x) / indent_threshold)
        
        # インデントレベルに応じて引用ブロックに変換
        if indent_level > 0 and conversion_level != 'conservative':
            # Markdownの引用ブロック記法を適用
            result_lines.append('>' * indent_level + ' ' + line)
        else:
            result_lines.append(line)
    
    return result_lines
