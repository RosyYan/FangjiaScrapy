# -*- coding: utf-8 -*-
"""
@author: yzx
"""
import scrapy
from scrapy import signals
from selenium import webdriver

from FangjiaScrapy.items import FangtianxiaItem, HouseItemLoader
from utils.common import get_md5
from datetime import datetime
from scrapy.xlib.pydispatch import dispatcher
import os


class FangtianxiaSpider(scrapy.Spider):
    name = "fangtianxia"  # 爬虫名
    allowed_domains = ["gz.esf.fang.com"]  # 允许的域名
    start_urls = ["https://gz.esf.fang.com/"]  # 入口urls

    def __init__(self, **kwargs):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, 'tools\\chromedriver.exe')
        self.browser = webdriver.Chrome(executable_path=path)
        super(FangtianxiaSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self):
        # 当爬虫退出的时候关闭chrome
        print("spider closed")
        self.browser.quit()

    # 默认的解析方法
    def parse(self, response):
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        # each page
        sell_list = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for item in sell_list:
            sell_url = item.css("h4.clearfix a::attr(href)").extract_first()
            yield scrapy.Request(url=response.urljoin(sell_url), callback=self.parse_detail)

        # next page
        next_page = response.xpath("//div[@class='page_al']/p/a[contains(text(),'下一页')]/@href").extract()
        if next_page:
            yield scrapy.Request("https://gz.esf.fang.com" + next_page[0], callback=self.parse)

    def parse_detail(self, response):
        # 导入item文件
        house_item = FangtianxiaItem()
        item_loader = HouseItemLoader(item=FangtianxiaItem(), response=response)
        item_loader.add_value("url_id", get_md5(response.url))  # url为主键
        item_loader.add_value("url", response.url)
        print("房天下URL:" + response.url)
        item_loader.add_css('total_price', 'div.price_esf.sty1 i::text')  # 总价
        item_loader.add_css('unit_price', "div.trl-item1.w132 div.tt::text")  # 单价 ['19489元/平米']
        item_loader.add_css('community', "a#kesfsfbxq_A01_01_05::text")
        item_loader.add_css('area', "div#address.rcont a#kesfsfbxq_C03_07::text")
        item_loader.add_css('house_type', "div.trl-item1.w146 div.tt::text")
        item_loader.add_css('floor_area', "div.trl-item1.w182 div.tt::text")
        item_loader.add_css('sale_time', "div.cont.clearfix div:nth-last-child(1) .rcont::text")  # 挂牌时间
        item_loader.add_value('crawl_time', datetime.now())
        house_item = item_loader.load_item()
        yield house_item
