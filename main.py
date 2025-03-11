#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import time
from ocr import process_image
from utils import get_image_files

def main():
    """
    メイン関数：コマンドライン引数の処理とOCR処理の実行
    """
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='AppleのVisionフレームワークを使ったOCR')
    parser.add_argument('input_dir', help='画像ファイルが含まれるディレクトリ')
    parser.add_argument('--output_dir', help='テキストファイルの出力先ディレクトリ')
    parser.add_argument('--raw', action='store_true', help='OCR結果をそのまま出力（テキスト整形を行わない）')
    parser.add_argument('--combine', action='store_true', help='すべての画像のOCR結果を1つのファイルに統合する')
    parser.add_argument('--combine_file', default='combined.txt', help='統合ファイルの名前（デフォルト: combined.txt）')
    args = parser.parse_args()
    
    # 入力ディレクトリの確認
    if not os.path.isdir(args.input_dir):
        print(f"エラー: 指定されたディレクトリが存在しません: {args.input_dir}")
        return 1
    
    # 画像ファイルの取得
    image_files = get_image_files(args.input_dir)
    
    if not image_files:
        print(f"警告: 指定されたディレクトリに画像ファイルが見つかりませんでした: {args.input_dir}")
        return 0
    
    # 出力ディレクトリの設定
    output_dir = args.output_dir if args.output_dir else args.input_dir
    
    # 出力ディレクトリが存在しない場合は作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"出力ディレクトリを作成しました: {output_dir}")
    
    # 処理開始時間
    start_time = time.time()
    
    print(f"処理を開始します。画像ファイル数: {len(image_files)}")
    
    # 統合モードの場合の準備
    combined_text = ""
    combined_file = None
    if args.combine:
        combined_file = os.path.join(output_dir, args.combine_file)
        print(f"統合モード: すべてのテキストを {combined_file} に保存します")
    
    # 各画像の処理
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] 処理中: {image_file}")
        
        try:
            # OCR処理（テキスト整形の有無を指定）
            text = process_image(image_file, not args.raw)
            
            # 個別ファイルへの保存（統合モードでも個別ファイルは作成する）
            base_name = os.path.splitext(os.path.basename(image_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"保存完了: {output_file}")
            
            # 統合モードの場合、テキストを蓄積
            if args.combine:
                # ファイル名をヘッダーとして追加
                combined_text += f"\n\n# {base_name}\n\n"
                combined_text += text
                combined_text += "\n\n" + "-" * 80 + "\n\n"  # セパレータ
            
        except Exception as e:
            print(f"エラー: 処理中に例外が発生しました: {str(e)}")
    
    # 統合モードの場合、すべてのテキストを1つのファイルに保存
    if args.combine and combined_text:
        try:
            with open(combined_file, 'w', encoding='utf-8') as f:
                f.write(combined_text)
            print(f"\n統合ファイルを保存しました: {combined_file}")
        except Exception as e:
            print(f"エラー: 統合ファイルの保存中に例外が発生しました: {str(e)}")
    
    # 処理終了時間
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\n処理が完了しました。")
    print(f"処理時間: {elapsed_time:.2f}秒")
    print(f"処理ファイル数: {len(image_files)}")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
