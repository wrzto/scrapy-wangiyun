# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy import log

class WangyiyunPipeline(object):

    def __init__(self):
        client=MongoClient(settings['MONGODB_SERVER'],settings['MONGODB_PORT'])
        db=client[settings['MONGODB_DB']]
        self.collection=db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        valid=True
        for data in item:
            if data is None:
                valid=False
        if valid:
            song_info=[{
                "music_name":item['music_name'],
                "artist":item['artist'],
                "special":item['special'],
                "comments":item['comments'],
                "song_url":item['song_url']
            }]
            self.collection.insert(song_info)
            log.msg("Item wrote to MongoDB database %s/%s" %
                    (settings['MONGODB_DB'], settings['MONGODB_COLLECTION']),
                    level=log.DEBUG, spider=spider)

        return item
