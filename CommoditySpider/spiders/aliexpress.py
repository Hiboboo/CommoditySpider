# -*- coding: utf-8 -*-
import json
import logging
import operator
import re

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from CommoditySpider.items import ClassifyItem, HistoryItem, CommodityItem


class AliExpressSpider(scrapy.Spider):
    """
    爬取‘速卖通’外文网站所有商品信息，遵循robots协议。
    """
    name = "aliexpress"
    start_urls = [
        'https://www.aliexpress.com/all-wholesale-products.html'
    ]
    allowed_domain = ['aliexpress.com/']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_departments, dont_filter=True)

    def parse_departments(self, response):
        """
        第一步：爬取网站内所有的公共商品类别，包括最上级到最末级的所有分类
        :param response: 包含有主页数据的结果
        :return: 若非末级类别则返回该类别对象，否则继续发送新的Request爬取末级类别列表数据
        """
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            item_root_id = 100000
            sub_items = soup.find_all('ul', class_='sub-item-cont util-clearfix')
            for item_ul in sub_items:
                item_sub_id = 1000
                item_all_a = item_ul.find_all('a')
                for item_a in item_all_a:
                    # if operator.eq("Women's Bags", item_a.text):
                    #     yield Request(url='https:%s' % item_a['href'], callback=self.parse_woman_departments, meta={
                    #         'pid': item_root_id
                    #     }, dont_filter=True)
                    # "Men's Bags", "Backpacks", "Luggage & Travel Bags", "Functional Bags" 已爬取
                    words = [
                        'Tools & Accessories',
                        'Special Categories',
                        'Mobile Phone Accessories',
                        'Portable Audio & Video',
                        'Accessories & Parts',
                        'Cables & Connectors',
                        'Industrial Computer & Accessories'
                    ]
                    if item_a.text in words:
                        classify = ClassifyItem()
                        classify['cid'] = item_sub_id
                        classify['pid'] = item_root_id
                        classify['name'] = item_a.text
                        classify['url'] = 'https:%s' % item_a['href']
                        classify['type'] = 'ali-1212'
                        print(item_sub_id, item_root_id, item_a.text)
                        # yield classify
                        # yield Request(url='https:%s' % item_a['href'], callback=self.parse_page, meta={
                        #     'cls_id': item_sub_id
                        # }, dont_filter=True)
                    item_sub_id += 1
                item_root_id += 1
        except Exception as e:
            logging.error('aliexpress parse departments exception:', e.args)

    def parse_woman_departments(self, response):
        try:
            item_root_id = response.meta.get('pid')
            item_sub_id = 100
            soup = BeautifulSoup(response.text, 'lxml')
            for item_div in soup.find_all('div', class_='bc-cate-name bc-nowrap-ellipsis'):
                item_a = item_div.find('a')
                classify = ClassifyItem()
                classify['cid'] = item_sub_id
                classify['pid'] = item_root_id
                classify['name'] = item_a['title']
                classify['url'] = 'https:%s' % item_a['href']
                classify['type'] = 'ali'
                yield classify
                yield Request(url='https:%s' % item_a['href'], callback=self.parse_page, meta={
                    'cls_id': item_sub_id
                }, dont_filter=True)
                item_sub_id += 2
        except Exception as e:
            logging.error('aliexpress parse woman departments exception:', e.args)

    page_count = 0

    def parse_page(self, response):
        """
        解析列表页面，使用递归方式持续获取下一页列表，直到没有下一页为止。
        最终将拿到每个商品的详情页链接，并继续爬取详情页数据

        :param response: 包含每一个列表页源数据的请求结果
        :return: 持续不断的爬取列表中每个商品的详情链接，并继续新的Request爬取详情数据
        """
        soup = BeautifulSoup(response.text, 'lxml')
        ul_tag = soup.find("ul", id='list-items')
        if ul_tag is None:
            ul_tag = soup.find('div', id='list-items')
        li_tags = ul_tag.find_all('li')
        for li_tag in li_tags:
            product_id_tag = li_tag.find('input', class_='atc-product-id')
            if product_id_tag is not None:
                try:
                    # 产品ID
                    com_id = product_id_tag['value']
                    pic_tag = soup.find('img', class_=re.compile('picCore'))
                    com_img = pic_tag['src']
                    if com_img is None:
                        com_img = pic_tag['image-src']
                    com_vendidos_str = soup.find('span', class_='order-num').text

                    commodity = CommodityItem()
                    commodity['cid'] = com_id
                    item_product = soup.find('a', class_=re.compile('product'))
                    # 产品名称
                    commodity['name'] = item_product['title']
                    # 已售数量 这个数量是全季度所有的销量总和
                    commodity['vendidos'] = \
                        re.findall('\\d+', com_vendidos_str if len(re.findall('\\d+', com_vendidos_str)) > 0 else 0)[0]
                    # 价格
                    commodity['price'] = soup.find('span', class_='value').text
                    commodity['thumbnail'] = 'https://%s' % com_img
                    # 详情页地址
                    commodity['show_url'] = 'https:%s' % item_product['href']
                    # 所属的产品类别
                    commodity['cls_id'] = response.meta.get('cls_id')
                    yield commodity

                    self.page_count += 1
                    print('~' * 5, self.page_count, com_id, commodity.get('show_url'))

                    history_url = 'https://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?&productId=%s&type=default&page=1' % com_id
                    yield Request(history_url, callback=self.parse_history_orders, meta={
                        'cid': com_id,
                        'cur_page': int(1)
                    }, dont_filter=True)
                except Exception as e:
                    logging.error('aliexpress parse woman departments exception:', e.args)

        next_page = soup.find('a', class_=re.compile('page-next'))
        if next_page is not None:
            yield Request('https:%s' % next_page['href'], callback=self.parse_page, meta=response.meta,
                          dont_filter=True)

    def parse_history_orders(self, response):
        history_json = json.loads(response.text)
        meta_data = response.meta
        records = history_json.get('records')
        for record in records:
            try:
                history = HistoryItem()
                history['id'] = record.get('id')
                history['cid'] = meta_data.get('cid')
                history['country_code'] = record.get('countryCode')
                history['country_name'] = record.get('countryName')
                history['quantity'] = record.get('quantity')
                history['unit'] = record.get('unit')
                history['date'] = record.get('date')
                yield history
            except Exception as e:
                logging.error('aliexpress parse history orders exception:', e.args)
        try:
            # current = history_json.get('page').get('current')
            # cur_page = int(current if len(str(current).strip()) == 0 or current is None else 1)
            cur_page = meta_data.get('cur_page')
            total = history_json.get('page').get('total')
            max_page = int(total if len(str(total).strip()) == 0 or total is None else 1)
            if cur_page < max_page:
                id = meta_data.get('cid')
                cur_page += 1
                url = 'https://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?&productId={id}&type=default&page={page}'.format(
                    id=id, page=cur_page)
                logging.info('-' * 5, url)
                meta_data['cur_page'] = cur_page
                yield Request(url, callback=self.parse_history_orders, meta=meta_data, dont_filter=True)
        except Exception as e:
            logging.error('aliexpress parse history orders next page exception:', e.args)
