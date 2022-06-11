"""This module launches the "rss_news_reader" package.

Usage: rss_reader.py [-h] [--version] [--json] [--verbose] [--limit LIMIT] [--date [DATE]] [source]

Args:
    Positional arguments:
        source: url of the site to read rss news
    Optional arguments:
        --limit LIMIT: limits news topics if this parameter is provided
        --date [DATE]: Outputs news for the specified date
        --json: prints result as JSON in stdout. Find the JSON structure in the README file
        --verbose: outputs verbose status messages
        --version: prints version info and exits
        -h, --help: prints help message and exits

Note:
    'source' or '--date' must be specified.
    'source' (site address) must contain "http" or "https" and "://" symbols.
    Day and month from 01 to 09 in '--date' argument should start with 0.

Example:
    $ python3 rss_news_reader URL --limit 100 --verbose --json
    $ python3 rss_news_reader URL --limit 100 --date 20210102 --verbose --json
    $ python3 rss_news_reader --date 20210102 --limit 100 --verbose --json
    $ python3 rss_news_reader --version
"""

from rss_parser import rss_reader

if __name__ == "__main__":
    rss_reader.main()
