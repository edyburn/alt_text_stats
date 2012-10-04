Alt Text Stats
==============

A script for scraping URLs and analyzing img tags for common text description implementation errors. The following checks are performed for each `<img>` tag:
* Has an `alt` attribute
* Has a `title` attribute
* Has a `longdesc` attribute
* `alt` attribute empty
* `alt` attribute exactly matches the image filename
* `alt` attribute exactly matches the `title` attribute
* `longdesc` attribute empty
* `longdesc` attribute refers to an anchor
* `longdesc` attribute is not a URL
* `longdesc` attribute refers to a URL that produces an error
* `longdesc` attribute exactly matches the `src` attribute
* `longdesc` attribute exactly matches the page's URL
* `longdesc` attribute exactly matches the domain
* `longdesc` attribute exactly matches the `href` attribute of the `<a>` that contains the image
The script outputs data for each image and aggregated by URL as two files.

Requirements
------------
* [requests](http://pypi.python.org/pypi/requests)
* [html5lib](http://pypi.python.org/pypi/html5lib)

Variables
---------
The `URL_FILE` variable is the path a CSV file containing the URLs to scrape in the second column. The script will only scrape the first 200 URLs. The `OUTPUT_AGGREGATE_FILE` variable is the path to save the aggregate results as a tab-delimited file. The `OUTPUT_DETAIL_FILE` variable is the path to save the detailed results (data for each image) as a tab-delimited file.

Usage
----
1. Open a Python interpreter
2. Run `import alt_text_stats`
3. Put the CSV file containing URLs in the correct location, or change the `alt_text_stats.URL_FILE` variable
4. Run `generate_stats()`
5. View the output files

