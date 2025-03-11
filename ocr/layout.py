"""
レイアウト解析モジュール

テキストのレイアウトを解析し、適切なMarkdown形式に変換する機能を提供します。
"""

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
