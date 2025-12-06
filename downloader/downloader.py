import os
import threading
import time
from queue import Queue
from typing import Dict, Iterable

import requests

from utils import resolve_filepath


def download(url, queue, filepath, timeout, max_retries, retry_backoff):
    try:
        print(f"[Producer] Downloading: {url}")
        last_exc = None
        attempts = max_retries + 1
        for attempt in range(1, attempts + 1):
            try:
                response = requests.get(url, timeout=timeout)
                response.raise_for_status()
                queue.put((url, response, filepath))
                print(f"[Producer] Done: {url}")
                return
            except Exception as e:
                last_exc = e
                if attempt < attempts:
                    sleep_for = retry_backoff * (2 ** (attempt - 1))
                    print(
                        f"[Producer] Retry {attempt}/{attempts - 1} for {url} in "
                        f"{sleep_for:.1f}s due to: {e}"
                    )
                    time.sleep(sleep_for)
        print(f"[Producer] Error downloading {url}: {last_exc}")
    except Exception as e:
        print(f"[Producer] Error downloading {url}: {e}")


def save(queue: Queue, skip_existing: bool):
    while True:
        item = queue.get()
        if item is None:
            queue.task_done()
            break

        url, response, filepath = item

        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.isdir(dirpath):
            try:
                os.makedirs(dirpath, exist_ok=True)
            except Exception as e:
                print(f"[Consumer] Error creating directory {dirpath}: {e}")
                queue.task_done()
                continue

        if skip_existing and os.path.exists(filepath):
            print(f"[Consumer] Skipped (exists): {filepath}")
            queue.task_done()
            continue

        try:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"[Consumer] Saved: {filepath}")
        except Exception as e:
            print(f"[Consumer] Error saving {filepath}: {e}")

        queue.task_done()


def build_url_to_path(urls, out_dir: str, preserve_path: bool) -> Dict[str, str]:
    return {u: resolve_filepath(u, out_dir, preserve_path) for u in urls}


def run_downloads(
    urls: Iterable[str],
    out_dir: str,
    preserve_path: bool,
    skip_existing: bool,
    producers: int,
    consumers: int,
    timeout: float,
    max_retries: int,
    retry_backoff: float,
):
    os.makedirs(out_dir, exist_ok=True)

    url_to_path = build_url_to_path(urls, out_dir, preserve_path)

    if skip_existing:
        to_download = [u for u in urls if not os.path.exists(url_to_path[u])]
        skipped = len(list(urls)) - len(to_download)
        if skipped:
            print(f"Skipping {skipped} existing file(s).")
    else:
        to_download = list(urls)

    if not to_download:
        print("Nothing to download.")
        return

    queue: Queue = Queue()
    consumer_threads = []
    producer_threads = []

    for _ in range(consumers):
        t = threading.Thread(target=save, args=(queue, skip_existing), daemon=True)
        t.start()
        consumer_threads.append(t)

    for url in to_download:
        filepath = url_to_path[url]
        t = threading.Thread(
            target=download,
            args=(url, queue, filepath, timeout, max_retries, retry_backoff),
        )
        t.start()
        producer_threads.append(t)

    for t in producer_threads:
        t.join()

    for _ in range(consumers):
        queue.put(None)

    queue.join()
    print("All downloads completed.")