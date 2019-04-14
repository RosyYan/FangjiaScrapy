# -*- coding: utf-8 -*-
"""
@author: yzx
"""
import scrapy

from FangjiaScrapy.items import AnjukeItem, HouseItemLoader
from datetime import datetime
from utils.common import get_md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class AnjukeSpider(scrapy.Spider):
    name = "anjuke"  # 爬虫名
    allowed_domains = ["guangzhou.anjuke.com"]  # 允许的域名
    start_urls = ["https://guangzhou.anjuke.com/sale/?from=navigation"]  # 入口urls

    def __init__(self, **kwargs):
        self.browser = webdriver.Chrome(executable_path='F:/Download/selenium/chromedriver.exe')
        super(AnjukeSpider, self).__init__()
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

        # each page
        sell_nodes = response.xpath("//ul[@id='houselist-mod-new']/li")
        for node in sell_nodes:
            sell_url = node.css(".house-title a::attr(href)").extract_first('')
            yield scrapy.Request(url=response.urljoin(sell_url), callback=self.parse_detail)
        # next page
        next_page = response.xpath("//div[@class='multi-page']/a[@class='aNxt']/@href").extract()
        if next_page:
            yield scrapy.Request(url=next_page[0], callback=self.parse)

    def parse_detail(self, response):
            house_item = AnjukeItem()
            item_loader = HouseItemLoader(item=AnjukeItem(), response=response)
            item_loader.add_value("url_id", get_md5(response.url))  # url为主键
            item_loader.add_value("url", response.url)
            item_loader.add_css('total_price', ".clearfix.basic-info .light em::text")  # 总价
            item_loader.add_css('unit_price', ".houseInfo-detail-list li:nth-child(3) .houseInfo-content ::text")  # 单价
            item_loader.add_css('community', ".houseInfo-detail-list li:nth-child(1) .houseInfo-content a::text")  # 小区名
            item_loader.add_css('area', ".houseInfo-detail-list li:nth-child(4) .houseInfo-content a::text")  # 所在区域
            item_loader.add_css('house_type', ".houseInfo-detail-list li:nth-child(2) .houseInfo-content ::text")  # 户型
            item_loader.add_css('floor_area', ".houseInfo-detail-list li:nth-child(5) .houseInfo-content ::text")  # 占地面积
            item_loader.add_xpath('sale_time', "//span[@class='house-encode']/text()")  # 挂牌时间
            item_loader.add_value('crawl_time', datetime.now())
            house_item = item_loader.load_item()
            print('finish')
            yield house_item
