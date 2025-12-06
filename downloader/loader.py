import os
import sys
import csv
import json
import xml.etree.ElementTree as ET
from typing import Set, Optional

import requests

from utils import is_valid_url


def load_from_file_lines(path: str) -> Set[str]:
    urls: Set[str] = set()
    if not os.path.isfile(path):
        print(f"URL file not found: {path}")
        return urls
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and is_valid_url(line):
                urls.add(line)
    return urls


def load_from_stdin() -> Set[str]:
    urls: Set[str] = set()
    for line in sys.stdin:
        line = line.strip()
        if line and is_valid_url(line):
            urls.add(line)
    return urls


def load_from_csv(path: str, column: str) -> Set[str]:
    urls: Set[str] = set()
    if not os.path.isfile(path):
        print(f"CSV file not found: {path}")
        return urls
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames or column not in reader.fieldnames:
            print(f"CSV column '{column}' not found in {path}. Columns: {reader.fieldnames}")
            return urls
        for row in reader:
            u = (row.get(column) or "").strip()
            if u and is_valid_url(u):
                urls.add(u)
    return urls


def load_from_json(path: str, key: Optional[str]) -> Set[str]:
    urls: Set[str] = set()
    if not os.path.isfile(path):
        print(f"JSON file not found: {path}")
        return urls
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to parse JSON from {path}: {e}")
        return urls

    def add_url(val):
        if isinstance(val, str) and is_valid_url(val):
            urls.add(val)

    def get_by_keypath(obj, keypath: str):
        parts = keypath.split(".")
        cur = obj
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    if isinstance(data, list):
        if all(isinstance(x, str) for x in data):
            for x in data:
                add_url(x)
        elif key:
            for item in data:
                if isinstance(item, dict):
                    val = get_by_keypath(item, key)
                    if isinstance(val, list):
                        for v in val:
                            add_url(v)
                    else:
                        add_url(val)
    elif isinstance(data, dict):
        if key:
            val = get_by_keypath(data, key)
            if isinstance(val, list):
                for v in val:
                    add_url(v)
            else:
                add_url(val)
        else:
            for v in data.values():
                if isinstance(v, str):
                    add_url(v)
                elif isinstance(v, list):
                    for vv in v:
                        add_url(vv)
    return urls


def load_from_sitemap(source: str, timeout: float) -> Set[str]:
    urls: Set[str] = set()
    try:
        if is_valid_url(source):
            resp = requests.get(source, timeout=timeout)
            resp.raise_for_status()
            content = resp.content
        else:
            if not os.path.isfile(source):
                print(f"Sitemap not found: {source}")
                return urls
            with open(source, "rb") as f:
                content = f.read()

        root = ET.fromstring(content)
        for elem in root.iter():
            if isinstance(elem.tag, str) and elem.tag.lower().endswith("loc"):
                if elem.text:
                    u = elem.text.strip()
                    if is_valid_url(u):
                        urls.add(u)
    except Exception as e:
        print(f"Failed to load sitemap {source}: {e}")
    return urls


def load_urls(args) -> Set[str]:
    urls: Set[str] = set()

    if args.urls:
        for u in args.urls:
            if is_valid_url(u):
                urls.add(u)
            else:
                print(f"Ignored invalid URL: {u}")

    if args.file:
        urls |= load_from_file_lines(args.file)

    if args.stdin:
        urls |= load_from_stdin()

    if args.csv:
        urls |= load_from_csv(args.csv, args.csv_column)

    if args.json:
        urls |= load_from_json(args.json, args.json_key)

    if args.sitemap:
        urls |= load_from_sitemap(args.sitemap, args.timeout)

    return urls