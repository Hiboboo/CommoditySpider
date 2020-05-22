# -*- coding: utf-8 -*-
import json
import random
import re
import string

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from CommoditySpider.items import ClassifyItem


class AliExpressSpider(scrapy.Spider):
    """
    爬取‘速卖通’外文网站所有商品信息，遵循robots协议。
    """
    name = "aliexpress"
    start_urls = [
        'https://www.aliexpress.com/all-wholesale-products.html?spm=a2g0o.home.16005.1.39a62963q1meLl&switch_new_app=y'
    ]
    allowed_domain = ['aliexpress.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_departments, dont_filter=True)

    def generate_id(self, len=7):
        return ''.join(random.sample(string.digits + string.ascii_uppercase, len))

    def generate_classify(self, id, name, url):
        classify = ClassifyItem()
        classify['id'] = id
        classify['name'] = name
        classify['url'] = url
        classify['type'] = 'aliexpress'
        return classify

    def parse_departments(self, response):
        """
        第一步：爬取网站内所有的公共商品类别，包括最上级到最末级的所有分类
        :param response: 包含有主页数据的结果
        :return: 若非末级类别则返回该类别对象，否则继续发送新的Request爬取末级类别列表数据
        """
        soup = BeautifulSoup(response.text, 'lxml')
        sub_item_categorys = soup.find_all('div', class_='sub-item-cont-wrapper')
        for sub_item_category in sub_item_categorys:
            latest_categorys = sub_item_category.find_all('a')
            for category in latest_categorys:
                id = self.generate_id()
                name = str(category.text).strip()
                url = 'https:%s' % category['href']
                yield self.generate_classify(id, name, url)
                yield Request(url=url, callback=self.parse_page, dont_filter=True, meta={'cls_id': id})

    def parse_page(self, response):
        """
        解析列表页面，使用递归方式持续获取下一页列表，直到没有下一页为止。
        最终将拿到每个商品的详情页链接，并继续爬取详情页数据

        :param response: 包含每一个列表页源数据的请求结果
        :return: 持续不断的爬取列表中每个商品的详情链接，并继续新的Request爬取详情数据
        """
        soup = BeautifulSoup(response.text, 'lxml')
        meta = response.meta
        scripts = soup.find_all('script', {'type': 'text/javascript'})
        for script in scripts:
            text = str(script.get_text()).strip()
            if re.match(r'^window.runParams', text):
                source = str(text.splitlines()[1]).strip()
                items = json.loads(source[source.find('{'):len(source) - 1]).get('items')
                for item in items:
                    cls_id = meta.get('cls_id')
                    id = item.get('productId')
                    name = item.get('title')
                    vendidos = item.get('tradeDesc')
                    price = item.get('price')
                    url = 'https:%s' % item.get('productDetailUrl')
                    thumbnail = 'https:%s' % item.get('imageUrl')
                    print('%s | %s | %s | %s | %s | %s | %s' % (cls_id, id, name, vendidos, price, url, thumbnail))
                    yield Request(url=url, callback=self.parse_ali_detail_page, meta=meta)

    def parse_ali_detail_page(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        scripts = soup.find_all('script')
        for script in scripts:
            text = str(script.get_text()).strip()
            if re.match(r'^window.runParams', text):
                source = json.loads(''.join(re.findall(':([^;]+)', text.splitlines()[1]))[:-1])
                id = source.get('pageModule').get('productId')
                name = source.get('pageModule').get('title')
