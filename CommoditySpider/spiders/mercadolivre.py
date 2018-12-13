# -*- coding: utf-8 -*-
import hashlib
import logging
import re

from bs4 import BeautifulSoup
from scrapy import Request

from CommoditySpider.items import *


class MercadoLivreSpider(scrapy.Spider):
    name = "mercado_livre"
    start_urls = [
        # 'https://www.mercadolivre.com.br/menu/departments'
        'https://www.mercadolivre.com.br/categories.html#menu=categories'
    ]
    allowed_domain = ['mercadolivre.com.br']

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse_departments, dont_filter=True)

    def parse(self, response):
        pass

    def parse_departments(self, response):
        """
        从源数据中解析所有的商品分类，并将其结果已数据对象的形式返回
        :param response: 商品分类数据源
        :return: 返回解析之后的所有商品分类数据，层级关系。
        """
        soup = BeautifulSoup(response.text, 'lxml')
        for span in soup.find_all('span', class_='ch-g1-3'):
            item_a = span.find('a')
            # 'Mochilas', 'Malas e Carteiras', 'Bolsas' 已爬取
            words = [
                'Acessórios para Áudio e Vídeo',
                'Fones de Ouvido',
                'Projetores e Telas',
                'Segurança para Casa',
                'Maquiagem',
                'Acessórios para Celulares'
            ]
            if item_a['title'] in words:
                title = item_a['title']
                classify = ClassifyItem()
                cls_id = hashlib.md5(title.encode(encoding='UTF-8')).hexdigest()
                classify['cid'] = cls_id
                classify['name'] = title
                classify['url'] = item_a['href']
                classify['count'] = re.findall('\\d+', span.text)[0]
                classify['type'] = 'mercado'
                yield classify
                yield Request(url=item_a['href'], callback=self.parse_content, meta={
                    'cls_id': cls_id
                }, dont_filter=True)

    def parse_content(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        # 查询所有的商品数据
        result_items = soup.find_all('li', class_=re.compile('results-item'))
        for result_item in result_items:
            try:
                id = result_item.find('div', class_='images-viewer')['item-id']
                condition = result_item.find('div', class_='item__condition').text
                location = condition.split('-')[1].strip() if '-' in condition else ''
                thumbnail = ''
                img_tag = result_item.find('img', class_='lazy-load')
                if img_tag is None:
                    img_id_tag = result_item.find('img', id=re.compile(id))
                    if img_id_tag is not None:
                        thumbnail = img_id_tag['data-src']
                else:
                    img_lazy_tag = result_item.find('img', class_='lazy-load')
                    if img_lazy_tag is not None:
                        thumbnail = img_lazy_tag['src']
                detail_url = result_item.find('a', class_=re.compile('item__js-link'))['href']
                data = {
                    'meta': response.meta,
                    'good_id': id,
                    'location': location,
                    'thumbnail': thumbnail,
                    'show_url': detail_url
                }
                yield Request(url=detail_url, callback=self.parse_detail, meta=data, dont_filter=True)
            except Exception as e:
                logging.error('mercado parse content exception:', e.args)

        next = soup.find('link', class_='andes-pagination__link', rel='next')
        if next is not None:
            yield Request(url=next['href'], callback=self.parse_content, meta=response.meta, dont_filter=True)

    count = 0

    def parse_detail(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            data = response.meta

            c_name = soup.find('h1', class_='item-title__primary').text
            c_vendidos = soup.find('div', class_='item-conditions').text
            c_4m_vendidos = soup.find('dd', class_='reputation-relevant').find('strong').text
            price_tag = soup.find_all('span', class_='price-tag-symbol')[-1]

            commodity = CommodityItem()
            commodity['cid'] = data.get('good_id')
            commodity['name'] = str(c_name).strip()
            commodity['vendidos'] = re.findall('\\d+', c_vendidos)[0] if len(re.findall('\\d+', c_vendidos)) > 0 else 0
            commodity['month_vendidos'] = c_4m_vendidos
            commodity['location'] = data.get('location')
            commodity['price_symbol'] = str(price_tag.text).strip()
            commodity['price'] = price_tag['content']
            commodity['thumbnail'] = data.get('thumbnail')
            commodity['show_url'] = data.get('show_url')
            commodity['cls_id'] = data.get('meta').get('cls_id')
            self.count += 1
            print('-----', self.count, data.get('good_id'), response.url)
            yield commodity
        except Exception as e:
            logging.error('mercado parse detail exception:', e.args)
