Parallel File Downloader

A simple Python script to download files from URLs using a producer-consumer model with multiple threads.

Features:
- Download multiple files in parallel
- Supports URLs from command line or text file
- Saves files into a specified output folder

Usage:

1. Download from URLs directly:
python main.py --urls https://example.com/file1.txt https://example.com/file2.jpg --out downloads

2. Download from a text file:
python main.py --file urls.txt --out downloads

3. Example with all arguments:s
python main.py --urls https://example.com/file1.txt https://example.com/file2.jpg --file urls.txt --out downloads --producers 4 --consumers 2

Arguments:

--urls             : Provide one or more URLs on the command line.
--file             : Path to a text file with one URL per line.
--stdin            : Read URLs from standard input (one URL per line).
--csv              : Read URLs from a CSV file.
--csv-column       : CSV column name that contains URLs (default: url).
--json             : Read URLs from a JSON file.
--json-key         : Dotted key path to extract URL(s) from JSON (e.g., items.pictures).
--sitemap          : Path or URL to an XML sitemap; extracts <loc> entries.
--out              : Output directory where downloaded files are saved.
--preserve-path    : Preserve the URL path structure under the output directory.
--skip-existing    : Skip downloading if the destination file already exists.
--producers        : Number of producer (download) threads.
--consumers        : Number of consumer (save) threads.
--timeout          : HTTP request timeout in seconds.
--max-retries      : Number of retry attempts on download failure.
--retry-backoff    : Base seconds for exponential backoff between retries.
