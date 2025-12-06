import os
from urllib.parse import urlparse

DEFAULT_TIMEOUT = 15.0


def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False


def resolve_filepath(url: str, out_folder: str, preserve_path: bool) -> str:
    parsed = urlparse(url)
    if preserve_path:
        path = parsed.path.lstrip("/")
        if not path or path.endswith("/"):
            path = os.path.join(path, "downloaded_file")
        safe_path = os.path.normpath(path)
        if safe_path.startswith(".."):
            safe_path = safe_path.replace("..", "_")
        return os.path.join(out_folder, safe_path)
    else:
        filename = os.path.basename(parsed.path) or "downloaded_file"
        return os.path.join(out_folder, filename)