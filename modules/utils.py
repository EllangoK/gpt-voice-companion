import os


def ensure_dir_exists(path):
    """Checks if directory exists and creates it if it does not"""
    if not os.path.exists(path):
        os.makedirs(path)
