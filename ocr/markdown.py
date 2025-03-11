"""
Markdown変換モジュール

テキストをMarkdown形式に変換する機能を提供します。
"""

import re

def convert_to_markdown(text):
    """
    整形されたテキストをMarkdown形式に変換する
    - 見出しの検出
    - リストの検出
    - テキスト強調の検出
    
    Parameters:
    -----------
    text : str
        変換対象のテキスト
    
    Returns:
    --------
    str
        Markdown形式に変換されたテキスト
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
    
    Parameters:
    -----------
    line : str
        検出対象の行
    index : int
        行のインデックス
    lines : list
        テキストの行のリスト
    
    Returns:
    --------
    str
        見出しとして検出された場合はMarkdown形式の見出し、
        そうでない場合は元の行
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
    
    Parameters:
    -----------
    line : str
        検出対象の行
    
    Returns:
    --------
    str
        リストとして検出された場合はMarkdown形式のリスト、
        そうでない場合は元の行
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
    
    Parameters:
    -----------
    line : str
        検出対象の行
    
    Returns:
    --------
    str
        テキスト強調が検出された場合はMarkdown形式の強調テキスト、
        そうでない場合は元の行
    """
    # 「」や『』で囲まれたテキストを強調として検出
    line = re.sub(r'「([^」]+)」', r'**\1**', line)
    line = re.sub(r'『([^』]+)』', r'*\1*', line)
    
    # 全角の*や_で囲まれたテキストも強調として検出
    line = re.sub(r'＊([^＊]+)＊', r'**\1**', line)
    line = re.sub(r'＿([^＿]+)＿', r'*\1*', line)
    
    return line
