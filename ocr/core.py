"""
OCR処理の中核モジュール

AppleのVisionフレームワークを使用して、画像からテキストを抽出する機能を提供します。
"""

from Foundation import NSURL
from Vision import VNRecognizeTextRequest, VNImageRequestHandler, VNRequestTextRecognitionLevelAccurate
from Quartz import CIImage
import os

# 他のモジュールをインポート
from .formatter import format_ocr_text
from .markdown import convert_to_markdown
from .table import detect_and_convert_tables
from .layout import analyze_and_convert_layout

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
    
    Returns:
    --------
    str
        抽出されたテキスト
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
