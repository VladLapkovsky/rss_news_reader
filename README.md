![check-code-coverage](https://img.shields.io/badge/code--coverage-51%25-orange)
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->

## Pure Python command-line RSS reader.

_**Python 3.9 is required.**_

RSS reader is a command-line utility which receives `source `or `--date [DATE]` arguments
and prints news in a human-readable format or stores them to the specified files.
It uses the `argparse` module.


The utility provides the following interface:

```
usage: rss_reader.py [-h] [--version] [--json] [--verbose] [--limit LIMIT]
[--date [DATE]] [--to-html TO_HTML] [--to-pdf TO_PDF] [--colorize] [source]

Pure Python command-line RSS reader.

positional arguments:
  source         RSS URL

optional arguments:
  -h, --help     Shows this help message and exits
  --version      Prints version info
  --json         Prints result as JSON in stdout
  --verbose      Outputs verbose status messages
  --limit LIMIT  Limits news topics if this parameter is provided
  --date [DATE]  Outputs news for the specified date
  --to-html TO_HTML: Saves news to .html file by the specified path
  --to-pdf TO_PDF: Saves news to .pdf file by the specified path
  --colorize: prints the console result of the utility in colorized mode
```

If the `source` argument is used, the RSS news articles are stored in a local 
storage in the `JSON` format while reading them from the web page. 
After that news articles are read from a local storage and printed.
**Note: `source` (site address) must contain `http` or `https` and `://` symbols.**

A local storage is located in a **current working directory**.

A local storage has the following structure (`publish date` has `%Y%m%d` format):

```
[
   {publish date: [news, news, news]},
   {publish date: [news, news, news]},
]
```

If the`--date `argument is used _without_ the `source` argument, utility prints news for the specified date from a local storage.
`--date` does not require Internet connection to fetch news from a local cache.
If the news or a local storage are not found, an error returns. 
**Note: you should run utility with the `source` argument at least one time to create a local storage.** 

If the`--date `argument is used _with_ the `source` argument, utility reads news **only** for the specified date from a web page.

The `--date ` argument takes a date in the `%Y%m%d` format. For example: `--date 20210102`.
**Note: day and month from 01 to 09 in the `--date` argument should start with 0.**

Examples of using the `--date` argument:

   ```sh
   $ python3 rss_reader.py {YOUR RSS URL} --date 20210102
   $ rss-reader --date 20210102 --limit 1
   ```

In case of using the `--json `argument, the utility converts the news into the `JSON` format. `JSON` news has the following structure:

```
{
    "feed": "a news feed",
    "title": "a news title",
    "date": "a news publish date",
    "link": "link to a news page",
    "description": "a news description",
    "links": {
        "[1]": "link to a news page (link)",
        "[2]": "link to a image in a news article (image)",
        "[3]": "... (image)",
    }
}
```
In case of using `--to-html` and `--to-pdf` arguments, the news will be saved to the files by the specified paths.
No news will be printed in stdout. But if `--json` is specified together with these options, 
then the `JSON` news will be printed to stdout, and converted file will contain news in the regular format.
`--date` also works with format converters and doesn't require Internet connection.

With the argument `--verbose` program prints all logs in stdout.

If `--date` and `--limit` arguments are not provided, all available news from a rss-page will be printed.

If `--limit` is larger than feed size then the program prints all available news.

The `--limit` and `--date` arguments also have influence on the `JSON` generation.

If the `--version` option is specified, the app prints its version and stops.

The `--colorize` argument affect only on console output.

The utility can be wrapped into distribution package with `setuptools`.
This package can export CLI utility named `rss-reader`.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

There is a list of libraries which are used to bootstrap the project.

* [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [requests](https://docs.python-requests.org/en/latest/)
* [lxml](https://lxml.de/)
* [pytest](https://docs.pytest.org/en/6.2.x/contents.html)
* [setuptools](https://setuptools.pypa.io/en/latest/)
* [python-dateutil](https://dateutil.readthedocs.io/en/stable/index.html)
* [build](https://pypa-build.readthedocs.io/en/latest/)
* [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/)
* [fpdf](https://pyfpdf.readthedocs.io/en/latest/)
* [colorama](https://pypi.org/project/colorama/)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Utility can be used in a few ways. 

First example:

1. Go to the folder with `rss_news_reader` folder.

2. Run below command (optional arguments write on your own):
   ```sh
   $ python3 rss_news_reader {YOUR RSS URL} --limit 1 --json --verbose
   ```
Second example:

1. Go to the `../rss_news_reader/rss_parser/` folder.

2. Run below command (optional arguments write on your own):
   ```sh
   $ python3 rss_reader.py {YOUR RSS URL} --limit 10 --json --verbose --to-html . --to-pdf {YOUR_PATH_TO_PDF_FILE}
   ```

Utility can be wrapped into distribution package with `setuptools`. This package can export `CLI` utility named `rss-reader`.
To do this, follow the steps:
1. Go to the `../rss_news_reader/` folder.
2. Run below command. This will create a distribution package (e.g. a `tar.gz` file and a `.whl` file in the `dist` directory), which can be upload to PyPI.

   ```sh
   $ python3 -m build
   ```
3. To export the CLI utility, run the command (the dot means current dir `/rss_news_reader/`) below.
Be sure that you have root rights to install packages.
   ```sh
   $ python3 -m pip install -e . 
   ```
4. To start the CLI utility, run the command (optional arguments write on your own) below:
   ```sh
   $ rss-reader {YOUR RSS URL} --limit 1 --json --verbose
   ```

`source`, `--date`, `--limit`, `--to-html`, `--to-pdf` can be used in a different combinations. For example:
   ```sh
   $ python3 rss_reader.py {YOUR RSS URL} --limit 1 --json --verbose
   $ python3 rss_reader.py {YOUR RSS URL} --date 20210102
   $ rss-reader --date 20210102 --limit 10 --verbose --to-html .
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->

## Contact

Vlad Lapkovsky - vladlapkovsky@gmail.com

Project Link: [https://github.com/VladLapkovsky/rss_news_reader](https://github.com/VladLapkovsky/rss_news_reader)

<p align="right">(<a href="#top">back to top</a>)</p>



[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge

[license-url]: https://github.com/VladLapkovsky/Homework/blob/master/VladLapkovsky/final_task/rss_news_reader/LICENSE.txt

[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555

[linkedin-url]: https://www.linkedin.com/in/vladislavlapkovsky/
