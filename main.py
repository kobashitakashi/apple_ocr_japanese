#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import time
import shutil
import datetime
from ocr import process_image
from utils import get_image_files

def main():
    """
    メイン関数：コマンドライン引数の処理とOCR処理の実行
    """
    # コマンドライン引数の設定
    parser = argparse.ArgumentParser(description='AppleのVisionフレームワークを使ったOCR')
    parser.add_argument('input_dir', help='画像ファイルが含まれるディレクトリ')
    parser.add_argument('--output_dir', help='テキストファイルの出力先ディレクトリ（指定しない場合は入力ディレクトリ直下の日時フォルダ）')
    parser.add_argument('--raw', action='store_true', help='OCR結果をそのまま出力（テキスト整形を行わない）')
    parser.add_argument('--combine', action='store_true', help='すべての画像のOCR結果を1つのファイルに統合する')
    parser.add_argument('--combine_file', help='統合ファイルの名前（指定しない場合は日時分秒）')
    parser.add_argument('--with-headers', action='store_true', help='統合ファイルにファイル名のヘッダーを追加する')
    parser.add_argument('--with-separators', action='store_true', help='統合ファイルにセパレータ（罫線）を追加する')
    parser.add_argument('--move-processed', action='store_true', help='処理済みの画像を_processedフォルダに移動する')
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
    
    # 現在の日時を取得（フォルダ名とファイル名に使用）
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    
    # 出力ディレクトリの設定
    if args.output_dir:
        # ユーザー指定の出力ディレクトリを使用
        base_output_dir = args.output_dir
        timestamp_dir = base_output_dir  # タイムスタンプディレクトリは作成しない
    else:
        # デフォルトは入力ディレクトリ直下の日時フォルダ
        base_output_dir = os.path.join(args.input_dir, timestamp)
        timestamp_dir = base_output_dir
        
        # タイムスタンプディレクトリが存在しない場合は作成
        if not os.path.exists(timestamp_dir):
            os.makedirs(timestamp_dir)
            print(f"タイムスタンプディレクトリを作成しました: {timestamp_dir}")
    
    # 出力テキストディレクトリの設定
    output_dir = os.path.join(timestamp_dir, "_output_texts")
    
    # 出力テキストディレクトリが存在しない場合は作成
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"出力テキストディレクトリを作成しました: {output_dir}")
    
    # 処理済み画像の移動先ディレクトリ
    processed_dir = None
    if args.move_processed:
        processed_dir = os.path.join(timestamp_dir, "_processed")
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
            print(f"処理済み画像ディレクトリを作成しました: {processed_dir}")
    
    # 処理開始時間
    start_time = time.time()
    
    print(f"処理を開始します。画像ファイル数: {len(image_files)}")
    
    # 統合モードの場合の準備
    combined_text = ""
    combined_file = None
    if args.combine:
        # 統合ファイル名の設定（指定がない場合は日時分秒）
        if args.combine_file:
            combine_filename = args.combine_file
        else:
            combine_filename = f"{timestamp}.md"
        
        combined_file = os.path.join(output_dir, combine_filename)
        print(f"統合モード: すべてのテキストを {combined_file} に保存します")
        
        # 統合ファイルのMarkdownメタデータ
        combined_text = f"""---
title: OCR結果統合ファイル
date: {now.strftime("%Y-%m-%d %H:%M:%S")}
source_files: {len(image_files)}
---

"""
    
    # 各画像の処理
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] 処理中: {image_file}")
        
        try:
            # OCR処理（テキスト整形の有無を指定）
            text = process_image(image_file, not args.raw)
            
            # 個別ファイルへの保存（統合モードでも個別ファイルは作成する）
            base_name = os.path.splitext(os.path.basename(image_file))[0]
            output_file = os.path.join(output_dir, f"{base_name}.md")
            
            # Markdownメタデータを追加
            md_content = f"""---
title: {base_name}
date: {now.strftime("%Y-%m-%d %H:%M:%S")}
source: {image_file}
---

{text}
"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"保存完了: {output_file}")
            
            # 統合モードの場合、テキストを蓄積
            if args.combine:
                # 空行を追加
                if i > 1:  # 最初のファイルの前には空行を追加しない
                    combined_text += "\n\n"
                
                # ファイル名のヘッダーを追加（オプション）
                if args.with_headers:
                    combined_text += f"# {base_name}\n\n"
                
                # テキストを追加
                combined_text += text
                
                # セパレータを追加（オプション）- Markdown形式の水平線
                if args.with_separators and i < len(image_files):  # 最後のファイルの後にはセパレータを追加しない
                    combined_text += "\n\n---\n"
            
            # 処理済み画像の移動
            if args.move_processed and processed_dir:
                try:
                    dest_file = os.path.join(processed_dir, os.path.basename(image_file))
                    shutil.move(image_file, dest_file)
                    print(f"画像を移動しました: {dest_file}")
                except Exception as e:
                    print(f"警告: 画像の移動中にエラーが発生しました: {str(e)}")
            
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
    print(f"結果は '{timestamp_dir}' ディレクトリに保存されました。")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
