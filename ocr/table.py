"""
表の検出と変換モジュール

テキスト内の表を検出し、Markdown形式の表に変換する機能を提供します。
"""

import re

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
