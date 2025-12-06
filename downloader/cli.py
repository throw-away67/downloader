import argparse

from utils import DEFAULT_TIMEOUT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Parallel file downloader.")
    parser.add_argument("--urls", nargs="*", help="List of URLs")
    parser.add_argument("--file", help="File with URLs (one per line)")
    parser.add_argument("--stdin", action="store_true", help="Read URLs from stdin (one per line)")
    parser.add_argument("--csv", help="CSV file containing URLs")
    parser.add_argument("--csv-column", default="url", help="CSV column name with URLs (default: url)")
    parser.add_argument("--json", help="JSON file containing URLs")
    parser.add_argument(
        "--json-key",
        help="Key or dotted path in JSON pointing to URL(s). If omitted, tries best-effort extraction.",
    )
    parser.add_argument("--sitemap", help="Sitemap path or URL to extract URLs from")

    parser.add_argument("--out", help="Output directory", default="downloaded")
    parser.add_argument(
        "--preserve-path",
        action="store_true",
        help="Preserve URL path structure under output directory",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip downloading files that already exist",
    )

    parser.add_argument("--producers", type=int, default=3, help="Number of producer (download) threads")
    parser.add_argument("--consumers", type=int, default=3, help="Number of consumer (save) threads")

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=0,
        help="Max retries per URL on failure (default: 0)",
    )
    parser.add_argument(
        "--retry-backoff",
        type=float,
        default=1.0,
        help="Base backoff seconds for retries (exponential)",
    )

    return parser