# -*- coding: utf-8 -*-

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

"""
    快速启动爬虫
    目的是在爬取 目标站点 之前, 先爬取代理网站的代理地址
"""

class SpiderManager(object):

    def __init__(self):
        self.setting = get_project_settings()
        self.process = None

    def start_spider(self):
        """ 在同一进程里面执行多个爬虫程序 """
        self.process = CrawlerProcess(self.setting)
        for spider in spider_list:
            self.process.crawl(spider)
        self.process.start()

    def start(self):
        """
        启动爬虫和代理池
        """
        self.start_spider()


if __name__ == '__main__':
    manager = SpiderManager()
    """
    Demospider() 是 Scrapy 项目 spider 目录下的爬虫脚本名字
    这里需要更换成 你项目的 爬虫名
    """
    # 'mercado_livre', 'aliexpress'
    spider_list = ['mercado_livre']
    manager.start()

# from scrapy.cmdline import execute
# #  -s JOBDIR=crawls/commspider-1
# execute(['scrapy', 'crawlall', 'commspider -s JOBDIR=crawls/commspider-1'])
