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
        return format_ocr_text(text)
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
