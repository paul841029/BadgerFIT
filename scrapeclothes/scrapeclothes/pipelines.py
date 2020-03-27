# -*- coding: utf-8 -*-
import scrapy
# from scrapy.exceptions import DropItem
import hashlib
import os.path
from termcolor import colored

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class ClothesPipeline(object):
    def open_spider(self, spider):
        # save output images to this directory:
        self.directory = 'output'

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

    def close_spider(self, spider):
        pass

    async def process_item(self, item, spider):
        filenames = []
        for i, url in enumerate(item['imgs']):
            request = scrapy.Request(url)
            response = await spider.crawler.engine.download(request, spider)

            if response.status != 200:
                # Error happened
                print(colored('Error downloading url %s' % url, 'red'))
                # raise DropItem('Error downloading image %s' % item)
                continue  # ??

            # Save img to file,
            # filename will be: <brand>-<productID>-<index>-<7 char of hash of url>.
            url_hash = hashlib.md5(url.encode("utf8")).hexdigest()[0:7]
            filename = "{}-{}-{}-{}.jpg".format(
                item['brand'], item['productID'], i, url_hash)
            file_path = os.path.join(self.directory, filename)
            with open(file_path, "wb") as f:
                f.write(response.body)

            filenames.append(filename)

        item['filenames'] = filenames
        return item
