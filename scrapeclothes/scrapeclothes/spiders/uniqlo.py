# -*- coding: utf-8 -*-
import scrapy
import json
from scrapeclothes.items import Cloth


class UniqloSpider(scrapy.Spider):
    name = 'uniqlo'
    allowed_domains = ['uniqlo.com']

    start_urls = [
        'https://www.uniqlo.com/us/en/women/t-shirts-and-tops/essential-tees',
        'https://www.uniqlo.com/us/en/women/t-shirts-and-tops/fashion-tees',
        'https://www.uniqlo.com/us/en/women/t-shirts-and-tops/active-tees',
        'https://www.uniqlo.com/us/en/women/t-shirts-and-tops/polos',
    ]

    def parse(self, response):
        title = response.css('.l3framework-main::text')

        # list of product links
        # product_links = response.css('.product-name a.name-link::attr(href)')
        # for product_link in product_links:
        #     yield response.follow(product_link, callback=self.parse_product)
        yield from response.follow_all(css='.product-name a.name-link', callback=self.parse_product)

    def parse_product(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        cloth = Cloth(brand='uniqlo')
        cloth['originalUrl'] = response.url

        cloth['name'] = extract_with_css(
            '#product-content .product-name::text')
        cloth['productID'] = extract_with_css(
            '#product-content .product-number span::text')

        thumbnails = response.css(
            '#main #thumbnails img.productthumbnail::attr(src)').getall()
        cloth['imgs'] = [thumbnail.replace(
            '?width=60', '?width=2000') for thumbnail in thumbnails]

        variations = response.css(
            '#main .product-variations .attribute .swatches.color .swatchanchor::attr(data-lgimg)').getall()
        cloth['variations'] = [json.loads(variation)
                               for variation in variations]

        return cloth
