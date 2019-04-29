# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst
from settings import SQL_DATETIME_FORMAT
import re


class HouseItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


def date_convert(value):
    reg = re.search('(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})[日]*', value)
    if reg:
        val = reg.group(1) + '-' + reg.group(2) + '-' + reg.group(3)
        try:
            create_date = datetime.datetime.strptime(val, "%Y-%m-%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        return create_date
    else:
        create_date = datetime.datetime.now().date()
        return create_date


def filter_unit(val):
    if val:
        return val.strip('元/m²|元/平方米|元/平米|平方米|平米|㎡')
    else:
        return 0


def filter_space(val):
    if val:
        value = re.findall('\S+', val)
        return ''.join(value)


class LianjiaItem(scrapy.Item):
    url_id = scrapy.Field()
    url = scrapy.Field()
    total_price = scrapy.Field()
    unit_price = scrapy.Field()
    community = scrapy.Field()
    area = scrapy.Field()
    house_type = scrapy.Field()
    floor_area = scrapy.Field(input_processor=MapCompose(filter_unit))
    sale_time = scrapy.Field(input_processor=MapCompose(date_convert))
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lianjia(url_id, url, total_price, unit_price, floor_area, 
            house_type, area, community, sale_time, crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
            on duplicate key update total_price=values(total_price),
            unit_price=values(unit_price)
        """
        params = (
            self['url_id'], self['url'], self['total_price'], self['unit_price'], self['floor_area'],
            self['house_type'],
            self['area'], self['community'], self['sale_time'], self['crawl_time'].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params


class AnjukeItem(scrapy.Item):
    url_id = scrapy.Field()
    url = scrapy.Field()
    total_price = scrapy.Field()
    unit_price = scrapy.Field(input_processor=MapCompose(filter_unit, filter_space))
    community = scrapy.Field()
    area = scrapy.Field()
    house_type = scrapy.Field(input_processor=MapCompose(filter_space))
    floor_area = scrapy.Field(input_processor=MapCompose(filter_unit))
    sale_time = scrapy.Field(input_processor=MapCompose(lambda x: x.replace("发布时间：", ''), date_convert))
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into anjuke(url_id, url, total_price, unit_price, floor_area, house_type, area, community, sale_time, crawl_time)
            values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update total_price=values(total_price),
            unit_price=values(unit_price)
        """
        params = (
            self['url_id'], self['url'], self['total_price'], self['unit_price'],
            self['floor_area'], self['house_type'], self['area'], self['community'],
            self['sale_time'], self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )
        return insert_sql, params


class FangtianxiaItem(scrapy.Item):
    url_id = scrapy.Field()
    url = scrapy.Field()
    total_price = scrapy.Field()
    unit_price = scrapy.Field(input_processor=MapCompose(filter_unit))
    community = scrapy.Field()
    area = scrapy.Field(input_processor=MapCompose(filter_space))
    house_type = scrapy.Field(input_processor=MapCompose(filter_space))
    floor_area = scrapy.Field(input_processor=MapCompose(filter_unit))
    sale_time = scrapy.Field(input_processor=MapCompose(filter_space))
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                insert into fangtianxia(url_id, url, total_price, unit_price, floor_area, house_type, area, community, sale_time, crawl_time)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) on duplicate key update total_price=values(total_price),
                unit_price=values(unit_price)
            """
        params = (
            self['url_id'], self['url'], self['total_price'], self['unit_price'], self['floor_area'],
            self['house_type'],
            self['area'], self['community'], self['sale_time'], self['crawl_time'].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params


class JiayuanItem(scrapy.Item):
    url_id = scrapy.Field()
    url = scrapy.Field()
    total_price = scrapy.Field()
    floor_area = scrapy.Field()
    unit_price = scrapy.Field()
    intermediary = scrapy.Field()
    area = scrapy.Field()
    house_type = scrapy.Field(input_processor=MapCompose(filter_space))
    sale_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into jiayuan(url_id, url, total_price, unit_price, floor_area, 
            house_type, area, intermediary, sale_time, crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) 
            on duplicate key update total_price=values(total_price),
            unit_price=values(unit_price)
        """
        self['unit_price'] = float(self['total_price']) / float(self['floor_area']) * 10000
        params = (
            self['url_id'], self['url'], self['total_price'], self['unit_price'], self['floor_area'],
            self['house_type'],
            self['area'], self['intermediary'], self['sale_time'], self['crawl_time'].strftime(SQL_DATETIME_FORMAT))
        return insert_sql, params
