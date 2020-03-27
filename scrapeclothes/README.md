# Scrapy to scrape clothes

## install

```sh
pip install scrapy termcolor
```

(at this moment scrapy version is 2.0.0)

## run to scrape images

run these commands in the same directory of this README (same directory as the `scrapy.cfg` file)

```sh
scrapy crawl uniqlo -o uniqlo.json
```

images will be in a new `output/` directory.

