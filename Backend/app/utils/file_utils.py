import os
from typing import Optional

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def allowed_file(filename: str, allowed_exts: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_exts

def get_ext(filename: str) -> str:
    if "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()
