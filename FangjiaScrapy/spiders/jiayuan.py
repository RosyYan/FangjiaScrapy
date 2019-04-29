# -*- coding: utf-8 -*-
from datetime import datetime

from items import HouseItemLoader, JiayuanItem
from utils.common import get_md5

__author__ = 'yzx'

import scrapy
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import re
import os


class JiayuanSpider(scrapy.Spider):
    name = "jiayuan"  # 爬虫名
    allowed_domains = ["www.gzcc.gov.cn"]  # 允许的域名
    start_urls = ["http://www.gzcc.gov.cn/data/QueryService/Query.aspx?QueryID=26"]  # 入口urls

    def __init__(self, **kwargs):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, 'tools\\chromedriver.exe')
        self.browser = webdriver.Chrome(executable_path=path)
        super(JiayuanSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        if response.url == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        print('Into parse:'+response.url)
        # print(response.text)
        head_url = response.url
        # next_page
        page_info = response.css("span.disabled::text").extract_first()
        print(page_info)
        if page_info:
            pages = page_info.split('/')[1]
            pages = re.findall('\d+', pages)[0]  # 总页数

            for i in range(1, int(pages)+1):
                next_url = response.urljoin(head_url+'&page='+str(i))
                print(next_url)
                yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_info)

    def parse_info(self, response):
        # each page
        print("debug jiayuan:" + response.url)
        sell_nodes = response.css("table.resultTable tbody tr")
        for sell_node in sell_nodes[1:]:
            house_item = JiayuanItem()
            item_loader = HouseItemLoader(item=JiayuanItem(), selector=sell_node, response=response)
            item_loader.add_css("url_id", "td:nth-child(2) a::text")  # 房源编号为主键
            item_loader.add_value("url", response.url)
            item_loader.add_css('total_price', "td:nth-child(5) a::text")  # 总价
            item_loader.add_css('intermediary', "td:nth-child(9) a::text")  # 中介机构
            item_loader.add_css('area', "td:nth-child(3) a::text")  # 所在区域
            item_loader.add_css('house_type', "td:nth-child(6) a::text")  # 户型
            item_loader.add_css('floor_area', "td:nth-child(7) a::text")  # 占地面积
            item_loader.add_css('sale_time', "td:nth-child(10) a::text")  # 挂牌时间
            item_loader.add_value('crawl_time', datetime.now())
            house_item = item_loader.load_item()
            yield house_item
