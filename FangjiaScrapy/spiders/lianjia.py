# -*- coding: utf-8 -*-
"""
@author: yzx
"""
import scrapy

from FangjiaScrapy.items import LianjiaItem, HouseItemLoader
from urllib import parse
from scrapy.http import Request
import re

from FangjiaScrapy.utils.common import get_md5
from datetime import datetime
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import os


class LianjiaSpider(scrapy.Spider):
    name = "lianjia"  # 爬虫名
    allowed_domains = ["gz.lianjia.com"]  # 允许的域名
    start_urls = ["https://gz.lianjia.com/ershoufang/"]  # 入口urls

    def __init__(self, **kwargs):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, 'tools\\chromedriver.exe')
        self.browser = webdriver.Chrome(executable_path=path)
        super(LianjiaSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()

    # 默认的解析方法
    def parse(self, response):
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")
        try:
            page_no = eval(response.css('.page-box.house-lst-page-box::attr(page-data)').extract_first(
                ""))  # {'totalPage': 100, 'curPage': 1}
            max_page = page_no.get('totalPage', '')
        except:
            max_page = 1
        for page in range(1, max_page):
            next_url = '/ershoufang/pg' + str(page)
            yield scrapy.Request(url=parse.urljoin(response.url, next_url), callback=self.parse_info)

    def parse_info(self, response):
        sell_nodes = response.css('.sellListContent .LOGCLICKDATA a')
        for sell_node in sell_nodes:
            sell_url = sell_node.css('::attr(href)').extract_first('')
            if re.match('https://gz.lianjia.com/ershoufang/\d+.html', sell_url):
                yield Request(url=parse.urljoin(response.url, sell_url), meta={"sell_url": sell_url},
                              callback=self.parse_detail)

    def parse_detail(self, response):

        house_item = LianjiaItem()

        # 通过自定义的ItemLoader加载item
        item_loader = HouseItemLoader(item=LianjiaItem(), response=response)
        item_loader.add_value("url_id", get_md5(response.url))  # url为主键
        item_loader.add_value("url", response.url)
        item_loader.add_css('total_price', 'span.total::text')  # 总价
        item_loader.add_css('unit_price', 'span.unitPriceValue::text')  # 单价
        item_loader.add_css('community', '.communityName .info::text')  # 小区名
        item_loader.add_css('area', '.areaName .info a::text')  # 所在区域
        item_loader.add_css('house_type', '.base .content li:nth-child(1)::text')  # 户型
        item_loader.add_css('floor_area', '.base .content li:nth-child(3)::text')  # 占地面积
        item_loader.add_css('sale_time', '.transaction .content li:nth-child(1) span:nth-child(2)::text')  # 挂牌时间
        item_loader.add_value('crawl_time', datetime.now())
        house_item = item_loader.load_item()
        yield house_item
