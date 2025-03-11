"""
テキスト整形モジュール

OCR結果のテキストを整形する機能を提供します。
"""

import re

def format_ocr_text(text):
    """
    OCR結果のテキストを整形する
    - 不要な改行を削除
    - 段落を適切に再構成
    
    Parameters:
    -----------
    text : str
        整形対象のテキスト
    
    Returns:
    --------
    str
        整形されたテキスト
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
