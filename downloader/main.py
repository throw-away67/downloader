from cli import build_parser
from loader import load_urls
from downloader import run_downloads


def main():
    parser = build_parser()
    args = parser.parse_args()

    urls = load_urls(args)
    if not urls:
        print("No URLs provided.")
        return

    run_downloads(
        urls=urls,
        out_dir=args.out,
        preserve_path=args.preserve_path,
        skip_existing=args.skip_existing,
        producers=args.producers,
        consumers=args.consumers,
        timeout=args.timeout,
        max_retries=args.max_retries,
        retry_backoff=args.retry_backoff,
    )


if __name__ == "__main__":
    main()