# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Cloth(scrapy.Item):
    # define the fields for your item here like:

    # product name, eg. WOMEN SUPIMA\u00ae COTTON CREW NECK SHORT-SLEEVE T-SHIRT
    name = scrapy.Field()
    # which brand is this from, eg. uniqlo
    brand = scrapy.Field()
    # original url requested
    originalUrl = scrapy.Field()
    # product ID or SKU#, eg. 422697
    productID = scrapy.Field()
    # a list of image urls, eg. ['https://xxx.xx/123/img1.png', ...]
    imgs = scrapy.Field()
    # list of objects for other colors or variations
    variations = scrapy.Field()
    # list of filenames after imgs are downloaded
    filenames = scrapy.Field()
