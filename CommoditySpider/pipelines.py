# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging

import pymysql
from scrapy import log

from CommoditySpider.items import ClassifyItem, HistoryItem, CommodityItem


# 目前所有的数据存储都是直接用的SQL拼接，以后要改成ORM管理方式

class CommodityspiderPipeline(object):
    def __init__(self):
        self.db = None
        self.cursor = None
        self.count = 0

    def open_spider(self, spider):
        self.db = pymysql.connect('127.0.0.1', 'root', '123456', 'mer_ali')
        self.cursor = self.db.cursor()
        logging.info('---Opened spider = %s' % spider.name)

    def close_spider(self, spider):
        self.cursor.close()
        self.db.close()
        logging.info('---Closed spider = %s' % spider.name)

    def remove_key(self, datas, keys):
        if not isinstance(datas, dict):
            return
        for key in list(datas.keys()):
            if key in keys:
                datas.pop(key)
        return datas

    def process_item(self, item, spider):
        try:
            if isinstance(item, ClassifyItem):
                self.save_classify(dict(item))
            if isinstance(item, CommodityItem):
                self.save_commodity(dict(item))
            if isinstance(item, HistoryItem):
                self.save_history_order(dict(item))
        except Exception as e:
            logging.error('%s process item exception:' % spider.name, e.args)

    def save_classify(self, values):
        table = 'classify'
        keys = 'cid, pid, name, url, count, type'
        sql = 'INSERT INTO {table}({keys}) VALUES {values} ON DUPLICATE KEY UPDATE name=VALUES(name), type=VALUES(type)'.format(
            table=table, keys=keys, values=(
                values.get('cid', ''),
                values.get('pid', '0'),
                values.get('name', ''),
                values.get('url', ''),
                values.get('count', 0),
                values.get('type', ''),
            ))
        self.__insert__(sql)

    def save_commodity(self, values):
        table = 'commodity'
        keys = 'cid, cls_id, name, vendidos, month_vendidos, location, price_symbol, price, thumbnail, show_url'
        sql = 'INSERT INTO {table}({keys}) VALUES {values} ON DUPLICATE KEY UPDATE vendidos=VALUES(vendidos), month_vendidos=VALUES(month_vendidos), price=VALUES(price)'.format(
            table=table, keys=keys, values=(
                values.get('cid', ''),
                values.get('cls_id', ''),
                values.get('name', ''),
                values.get('vendidos', '0'),
                values.get('month_vendidos', '0'),
                values.get('location', ''),
                values.get('price_symbol', ''),
                values.get('price', ''),
                values.get('thumbnail', ''),
                values.get('show_url', '')
            ))
        self.__insert__(sql)

    def save_history_order(self, values):
        table = 'history_order'
        keys = 'id, cid, country_code, country_name, name, quantity, unit'
        sql = 'INSERT INTO {table}({keys}) VALUES {values} ON DUPLICATE KEY UPDATE quantity=VALUES(quantity)'.format(
            table=table, keys=keys, values=(
                values.get('id', ''),
                values.get('cid', ''),
                values.get('country_code', ''),
                values.get('country_name', ''),
                values.get('name', ''),
                values.get('quantity', ''),
                values.get('unit', '')
            ))
        self.__insert__(sql)

    def __insert__(self, sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
            print(sql)
        except Exception as e:
            print('Failed', e)
            self.db.rollback()
