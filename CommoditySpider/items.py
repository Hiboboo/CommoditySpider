# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CommodityItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    vendidos = scrapy.Field()
    month_vendidos = scrapy.Field()
    price_symbol = scrapy.Field()
    price = scrapy.Field()
    thumbnail = scrapy.Field()
    show_url = scrapy.Field()
    cls_id = scrapy.Field()


class ClassifyItem(scrapy.Item):
    id = scrapy.Field()
    pid = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()


class HistoryItem(scrapy.Item):
    id = scrapy.Field()
    cid = scrapy.Field()
    country_name = scrapy.Field()
    country_code = scrapy.Field()
    quantity = scrapy.Field()
    unit = scrapy.Field()
    date = scrapy.Field()
