# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import json
import random
import re
import string

import requests
from bs4 import BeautifulSoup


def generate_id(len=7):
    return ''.join(random.sample(string.digits + string.ascii_uppercase, len))


def get_response(url):
    # 代理服务器
    proxyHost = "u1256.b5.t.16yun.cn"
    proxyPort = "6460"

    # 代理隧道验证信息
    proxyUser = "16UTSANJ"
    proxyPass = "814459"

    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    # 设置 http和https访问都是用HTTP代理
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }

    #  设置IP切换头
    tunnel = random.randint(1, 10000)
    headers = {"Proxy-Tunnel": str(tunnel)}
    return requests.get(url=url)


def parse_ali_page():
    url = 'https://www.aliexpress.com/all-wholesale-products.html?spm=a2g0o.home.16005.1.39a62963q1meLl&switch_new_app=y'
    parse_ali_departments(get_response(url))


def parse_ali_departments(response):
    soup = BeautifulSoup(response.text, 'lxml')
    sub_item_categorys = soup.find_all('div', class_='sub-item-cont-wrapper')
    for sub_item_category in sub_item_categorys:
        latest_categorys = sub_item_category.find_all('a')
        for category in latest_categorys:
            id = generate_id()
            name = str(category.text).strip()
            url = 'https:%s' % category['href']
            parse_ali_list_page(get_response(url))


def parse_ali_list_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    scripts = soup.find_all('script', {'type': 'text/javascript'})
    for script in scripts:
        text = str(script.get_text()).strip()
        if re.match(r'^window.runParams', text):
            source = str(text.splitlines()[1]).strip()
            items = json.loads(source[source.find('{'):len(source) - 1]).get('items')
            for item in items:
                id = item.get('productId')
                name = item.get('title')
                vendidos = item.get('tradeDesc')
                price = item.get('price')
                url = 'https:%s' % item.get('productDetailUrl')
                thumbnail = 'https:%s' % item.get('imageUrl')
                # parse_ali_detail_page(get_response(url))
                print('%s | %s | %s | %s | %s | %s' % (id, name, vendidos, price, url, thumbnail))


def parse_ali_detail_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    scripts = soup.find_all('script')
    for script in scripts:
        text = str(script.get_text()).strip()
        if re.match(r'^window.runParams', text):
            source = json.loads(''.join(re.findall(':([^;]+)', text.splitlines()[1]))[:-1])
            id = source.get('pageModule').get('productId')
            name = source.get('pageModule').get('title')


if __name__ == '__main__':
    print('产品ID\t名称\t销量\t价格\t链接\t图片')
    parse_ali_page()