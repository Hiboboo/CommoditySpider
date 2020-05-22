# -*- coding: utf-8 -*-
import logging
import random
import re
import string
import traceback

from bs4 import BeautifulSoup
from scrapy import Request

from CommoditySpider.items import *


class MercadoLivreSpider(scrapy.Spider):
    name = "mercado_livre"
    start_urls = [
        'https://www.mercadolivre.com.br/categorias#menu=categories'
    ]
    allowed_domain = ['mercadolivre.com.br']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_departments, dont_filter=True, errback=self.errback_httpbin)

    def errback_httpbin(self, failure):
        self.logger.error(repr(failure))

    def generate_id(self, len=7):
        return ''.join(random.sample(string.digits + string.ascii_uppercase, len))

    def generate_classify(self, id, name, url):
        classify = ClassifyItem()
        classify['id'] = id
        classify['name'] = name
        classify['url'] = url
        classify['type'] = 'mercado'
        return classify

    target_first_categorys = ['Acessórios para Veículos', 'Casa, Móveis e Decoração', 'Eletrodomésticos']
    # 需要爬取的目标分类
    target_categorys = ['Banheiros']

    def parse_departments(self, response):
        """
        从源数据中解析所有的商品分类，并将其结果已数据对象的形式返回
        :param response: 商品分类数据源
        :return: 返回解析之后的所有商品分类数据，层级关系。
        """
        soup = BeautifulSoup(response.text, 'lxml')
        for categorys in soup.find_all('div', class_='categories__container'):
            first_category = categorys.find('a', class_='categories__title')
            if str(first_category.text).strip() in self.target_first_categorys:
                yield self.generate_classify(self.generate_id(), first_category.text, first_category['href'])
                second_categorys = categorys.find_all('a', class_='categories__subtitle')
                for second_category in second_categorys:
                    id = self.generate_id(11)
                    url = second_category['href']
                    # if str(second_category.text).strip() in self.target_categorys:
                    yield self.generate_classify(id, second_category.text, url)
                    yield Request(url=url, callback=self.parse_content, meta={
                        'cls_id': id
                    }, dont_filter=True)

    def parse_content(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            ol = soup.find('ol', id='searchResults')
            if not ol is None:
                # 查询列表所有的商品数据
                ol_results = ol.find_all('li', class_=re.compile('results-item'))
                for li in ol_results:
                    try:
                        div_tag = li.find('div', class_='images-viewer')
                        img_tag = div_tag.find('img')
                        # thumbnail = img_tag['src' if ''.join(img_tag['class']) == 'lazy-load' else 'data-src']
                        show_url = div_tag['item-url']
                        data = {
                            'meta': response.meta,
                            'show_url': show_url,
                            'thumbnail': ''
                        }
                        yield Request(url=show_url, callback=self.parse_detail, meta=data, dont_filter=True)
                    except Exception as e:
                        logging.error('mercado parse content exception:', e.args)
                next = soup.find('link', class_='andes-pagination__link', rel='next')
                if next is not None:
                    yield Request(url=next['href'], callback=self.parse_content, meta=response.meta, dont_filter=True)
        except Exception:
            logging.error('AAA解析发生错误的链接：%s' % response.meta.get('url'))
            traceback.print_exc()

    count = 1

    def generate_commodity(self, cls_id, id, name, thumbnail, url, price_symbol, price, vendidos, month_vendidos):
        c = CommodityItem()
        c['id'] = id
        c['name'] = name
        c['vendidos'] = vendidos
        c['month_vendidos'] = month_vendidos
        c['price_symbol'] = price_symbol
        c['price'] = price
        c['thumbnail'] = thumbnail
        c['show_url'] = url
        c['cls_id'] = cls_id
        print('%s | %s | %s | %s | %s | %s | %s | %s | %s' % (
            self.count, cls_id, id, name, price_symbol + price, vendidos, month_vendidos, url, thumbnail))
        self.count += 1
        return c

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            meta = response.meta

            cls_id = meta.get('meta').get('cls_id')
            inputTag = soup.find('input', attrs={'name': 'itemId'})
            if not inputTag is None:
                id = inputTag['value']
                title = soup.find('h1', class_='item-title__primary')
                name = str(title.text).strip() if title is not None else '- -'
                thumbnail = meta.get('thumbnail')
                url = soup.find('input', attrs={'name': 'itemPermalink'})['value']
                price_tag = soup.find('span', class_='price-tag').find('span', class_='price-tag-symbol')
                price_symbol = price_tag.text
                price = price_tag['content']
                ven_tag = soup.find('div', class_='item-conditions')
                vendidos_text = ven_tag.text if ven_tag is not None else '0'
                vendidos = re.findall('\\d+', vendidos_text)[0] if len(re.findall('\\d+', vendidos_text)) > 0 else 0
                mon_ven_tag = soup.find('dd', class_='reputation-relevant')
                month_vendidos = mon_ven_tag.find('strong').text if mon_ven_tag is not None else 0
                yield self.generate_commodity(cls_id, id, name, thumbnail, url, price_symbol, price, vendidos,
                                              month_vendidos)
        except Exception:
            logging.error('解析发生错误的链接：%s' % response.meta.get('show_url'))
            traceback.print_exc()
