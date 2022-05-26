import os

def get_download_dir(path: str):
    if not os.path.isdir(path):
        os.mkdir(path)
    return os.path.abspath(path)
