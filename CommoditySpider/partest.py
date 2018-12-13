# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html


# data = {'cid': 'DSJ1U5C8',
#         'depth': 1,
#         'download_timeout': 180.0,
#         'name': 'Complementos de boda',
#         'permalink': 'https://es.aliexpress.com/category/100005624/wedding-accessories.html',
#         'pid': 'BII4PNB9',
#         'redirect_times': 1,
#         'redirect_ttl': 19,
#         'redirect_urls': ['https://es.aliexpress.com/category/100005624/wedding-accessories.html'],
#         'type': 'ALI_THIRD'}
#
#
# def remove_key(datas, keys):
#     if not isinstance(datas, dict):
#         return
#     for key in list(datas.keys()):
#         if key in keys:
#             datas.pop(key)
#     return datas


# print(remove_key(data, ['depth', 'download_timeout', 'redirect_times', 'redirect_ttl', 'redirect_urls']))
from scrapy import Request


def parse_page():
    # 假装里边有100个可用URL
    urls = [
        '',
    ]
    for url in urls:
        print(url) # 可以一次性把100个url全打印出来
        yield Request(url=url, callback=parse_content)


def parse_content(response):
    # 这里始终都是每秒甚至两秒才打印一次结果 Why？
    pass
