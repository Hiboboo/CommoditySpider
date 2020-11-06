# -*- coding: utf-8 -*-

# Scrapy settings for CommoditySpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'CommoditySpider'

SPIDER_MODULES = ['CommoditySpider.spiders']
NEWSPIDER_MODULE = 'CommoditySpider.spiders'

COMMANDS_MODULE = 'CommoditySpider.commands'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'text/html;charset=UTF-8',
    'Cache-Control': 'no-cache',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'CommoditySpider.middlewares.CommodityspiderSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'CommoditySpider.middlewares.CommodityspiderDownloaderMiddleware': 543,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    'CommoditySpider.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'CommoditySpider.pipelines.CommodityspiderPipeline': 300,
}

LOG_LEVEL = 'INFO'
LOG_FILE = "spider-1106-001.log"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.5 # 1=1s
# Configure maximum concurrent requests performed by Scrapy (default: 16) 开启线程数量
CONCURRENT_REQUESTS = 512
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 20
CONCURRENT_REQUESTS_PER_IP = 64
# The initial download delay 开始下载时限速并延迟时间
AUTOTHROTTLE_START_DELAY = 3
# 在高延迟的情况下设置的最大下载延迟
AUTOTHROTTLE_MAX_DELAY = 20
DOWNLOAD_TIMEOUT = 20
# The average number of requests Scrapy should be sending in parallel to each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 512

CONCURRENT_ITEMS = 512

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False
# 重试
RETRY_ENABLED = True
# 重定向
REDIRECT_ENABLED = True
AJAXCRAWL_ENABLED = True
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True

# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False
