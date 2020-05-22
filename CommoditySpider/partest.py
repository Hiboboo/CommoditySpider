# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import random
import re
import string

import requests
from bs4 import BeautifulSoup


def parse_page():
    r = requests.get('https://www.mercadolivre.com.br/categorias#menu=categories')
    parse_page_content(r)


def generate_id(len=7):
    return ''.join(random.sample(string.digits + string.ascii_uppercase, len))


target_first_categorys = ['Acessórios para Veículos', 'Casa, Móveis e Decoração', 'Eletrodomésticos']

target_categorys = ['Banheiros']


def parse_page_content(response):
    soup = BeautifulSoup(response.text, 'lxml')
    for categorys in soup.find_all('div', class_='categories__container'):
        first_category = categorys.find('a', class_='categories__title')
        if str(first_category.text).strip() in target_first_categorys:
            # print('【一级分类】ID=%s, 名称=%s, 链接=%s' % (generate_id(), first_category.text, first_category['href']))
            second_categorys = categorys.find_all('a', class_='categories__subtitle')
            for second_category in second_categorys:
                id = generate_id(9)
                # url = second_category['href']
                url = 'https://lista.mercadolivre.com.br/banheiros-torneiras-banheiro/'
                # print('\t【二级分类】ID=%s, 名称=%s, 链接=%s' % (id, second_category.text, url))
                # if str(second_category.text).strip() in target_categorys:
                #     parse_page_detail(url, id)
                print(second_category.text)


def parse_page_detail(url, cls_id):
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    ol = soup.find('ol', id='searchResults')
    try:
        for li in ol.find_all('li', class_=re.compile('results-item')):
            div_img_tag = li.find('div', class_='images-viewer').find('img')
            thumbnail = div_img_tag['src' if ''.join(div_img_tag['class']) == 'lazy-load' else 'data-src']
            show_url = li.find('a', class_=re.compile('item__info-link'))['href']
            parse_page_show(show_url, {
                'cls_id': cls_id,
                'thumbnail': thumbnail
            })
    except:
        print('解析页面出现错误：url=' + url)
    next = soup.find('link', class_='andes-pagination__link', rel='next')
    if next is not None:
        parse_page_detail(requests.get(next['href']), cls_id)


def parse_page_show(url, meta):
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    cls_id = meta.get('cls_id')
    id = soup.find('input', attrs={'name': 'itemId'})['value']
    name = str(soup.find('h1', class_='item-title__primary').text).strip()
    thumbnail = meta.get('thumbnail')
    url = soup.find('input', attrs={'name': 'itemPermalink'})['value']
    price_tag = soup.find('span', class_='price-tag').find('span', class_='price-tag-symbol')
    price_symbol = price_tag.text
    price = price_tag['content']
    vendidos_text = soup.find('div', class_='item-conditions').text
    vendidos = re.findall('\\d+', vendidos_text)[0] if len(re.findall('\\d+', vendidos_text)) > 0 else 0
    month_vendidos = soup.find('dd', class_='reputation-relevant').find('strong').text
    print('%s | %s | %s | %s | %s | %s | %s | %s' % (
        cls_id, id, name, price_symbol + price, vendidos, month_vendidos, url, thumbnail))


if __name__ == '__main__':
    # print('所属分类\tID\t名称\t价格\t销量\t月销量\t链接\t图片')
    parse_page()
    # url = 'https://produto.mercadolivre.com.br/MLB-767152551-torneira-cascata-banheiro-misturador-quadrada-dourada-parana-_JM#position=42&type=item&tracking_id=1318d260-6264-4b28-bfcb-3046062dd545'
    # meta = {"cls_id": '111', 'thumbnail': ""}
    # parse_page_show(url, meta)
