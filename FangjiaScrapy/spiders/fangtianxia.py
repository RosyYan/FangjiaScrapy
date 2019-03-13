# -*- coding: utf-8 -*-
"""
@author: yzx
"""
import scrapy

from FangjiaScrapy.items import FangtianxiaItem, HouseItemLoader
from utils.common import get_md5
from datetime import datetime
import FangjiaScrapy.utils.yundama_request
import urllib.request


class FangtianxiaSpider(scrapy.Spider):
    name = "fangtianxia"  # 爬虫名
    allowed_domains = ["gz.esf.fang.com"]  # 允许的域名
    start_urls = ["https://gz.esf.fang.com/"]  # 入口urls

    # 默认的解析方法
    def parse(self, response):
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")
        # 解决验证码识别问题
        if "captcha-verify" in response.url:
            captcha_image = response.css("#seccode::attr(src)").extract_first()
            if captcha_image:
                image_tuple = urllib.request.urlretrieve(url=response.urljoin(captcha_image),
                                                         filename="../utils/images/captcha.jpg")
                code = FangjiaScrapy.ydm(image_tuple[0])
                return scrapy.FormRequest.from_response(response,formdata={"code":code},callback=self.parse)

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
        item_loader.add_css('total_price', '.price_esf i::text')  # 总价
        item_loader.add_css('unit_price', '.tab-cont-right div:nth-child(2) .w132 .tt::text')  # 单价 ['19489元/平米']
        if item_loader.get_output_value('unit_price') is None:
            item_loader.add_css('unit_price', '.tab-cont-right div:nth-child(3) .w132 .tt::text')
            item_loader.add_css('community', ".tab-cont-right div:nth-child(5) div:nth-child(1) .rcont .blue::text")
            item_loader.add_css('area', ".tab-cont-right div:nth-child(5) div:nth-child(2) #address a::text")
            item_loader.add_css('house_type', '.tab-cont-right div:nth-child(3) .w146 .tt::text')
            item_loader.add_css('floor_area', '.tab-cont-right div:nth-child(3) .w182 .tt::text')
        else:
            item_loader.add_css('community',
                                ".tab-cont-right div:nth-child(4) div:nth-child(1) .rcont .blue::text")  # 小区名
            item_loader.add_css('area',
                                ".tab-cont-right div:nth-child(4) div:nth-child(2) #address a::text")  # 所在区域
            item_loader.add_css('house_type', '.tab-cont-right div:nth-child(2) .w146 .tt::text')  # 户型
            item_loader.add_css('floor_area', '.tab-cont-right div:nth-child(2) .w182 .tt::text')  # 占地面积
        item_loader.add_css('sale_time', '.fydes-item .cont ::text')  # 挂牌时间
        item_loader.add_value('crawl_time', datetime.now())
        house_item = item_loader.load_item()
        yield house_item
