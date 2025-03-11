import os

def get_image_files(directory):
    """
    指定されたディレクトリ内の画像ファイルを取得する
    """
    image_extensions = ['.png', '.jpg', '.jpeg', '.tiff']
    image_files = []
    
    for file in os.listdir(directory):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(directory, file))
    
    return sorted(image_files)
