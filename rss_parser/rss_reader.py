"""This module provides the main entrance to the command-line RSS reader.

Run this module in the command line to get rss-news.

Usage: rss_reader.py [-h] [--version] [--json] [--verbose] [--limit LIMIT]
[--date [DATE]] [--to-html TO_HTML] [--to-pdf TO_PDF] [--colorize] [source]

Positional arguments:
    source: url of the site to read rss news
Optional arguments:
    -h, --help: prints help message and exits

    --version: prints version info and exits

    --json: prints result as JSON in stdout. Find the JSON structure in the README file

    --verbose: outputs verbose status messages

    --limit LIMIT: limits news topics if this parameter is provided

    --date [DATE]: outputs news for the specified date

    --to-html TO_HTML: saves news to .html file by the specified path

    --to-pdf TO_PDF: saves news to .pdf file by the specified path

    --colorize: prints the console result of the utility in colorized mode

Note:
    'source' or '--date' must be specified.
    'source' (site address) must contain "http" or "https" and "://" symbols.
    Day and month from 01 to 09 in '--date' argument should start with 0.

Example:
    $ python3 rss_reader.py URL --limit 100 --verbose --json

    $ python3 rss_reader.py URL --limit 100 --date 20210102 --verbose --json

    $ python3 rss_reader.py --date 20210102 --limit 100 --verbose --json

    $ python3 rss_reader.py --version
"""

import os
import sys
import time

sys.path.append(os.path.abspath(os.pardir))  # Add rss_news_reader folder to the sys.path

from rss_parser.arg_parser import ArgsChecker, init_argparse
from rss_parser.logger import LOGGER
from rss_parser.parser_management import ParserManager
from rss_parser.web_parser.web_parser import WebParser


def main():
    """Run the rss_reader logic.

    Initialize "argparse" arguments from "arg_parser.py".
    Check the input parameters in the "ArgsChecker" class (look through "arg_parser.py" to see what has been checked).
    If some of parameters are wrong, the program prints the specific error message and exit.
    The input url transfers to the web parser, where the xml-page of rss-news is downloaded.
    The xml-page transfers to "ParserManager".
    Use the "start_processing" method of the "ParserManager" instance to start processing news.
    """
    start = time.perf_counter()
    args = init_argparse()
    LOGGER.setLevel("INFO" if args.verbose else "WARNING")
    LOGGER.info("logging system is on...")
    formats_and_paths_for_conversion = {"to_html": args.to_html, "to_pdf": args.to_pdf}
    try:
        ArgsChecker(
            url=args.url,
            limit=args.limit,
            date=args.date,
            formats_and_paths=formats_and_paths_for_conversion,
        ).check()
    except (ValueError, TimeoutError) as exception:
        LOGGER.warning(exception)
    else:
        path_values = [path for path in formats_and_paths_for_conversion.values() if path is not None]
        parser = ParserManager(
            xml_page=WebParser(url=args.url, parser_mode="xml").soup if args.url else None,
            json_flag=args.json,
            news_limit=args.limit,
            date=args.date,
            formats_and_paths=formats_and_paths_for_conversion if path_values else None,
            colorized_mode=args.colorize,
        )
        parser.start_processing()
        LOGGER.info("Program was completed in %.2f seconds.", time.perf_counter() - start)


if __name__ == "__main__":
    main()
