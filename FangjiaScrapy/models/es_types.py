# -*- coding: utf-8 -*-
__author__ = 'yzx'

from elasticsearch_dsl import DocType, Date, Keyword, Text, Double, Completion
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['localhost'])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class HouseType(DocType):
    suggest = Completion(analyzer=ik_analyzer)
    url_id = Keyword()  # 不用分词
    url = Keyword()
    total_price = Double()
    unit_price = Double()
    community = Text(analyzer="ik_max_word")
    area = Keyword()
    house_type = Keyword()
    floor_area = Double()
    sale_time = Date()

    class Meta:
        index = "lianjia"
        doc_type = "house"


if __name__ == '__main__':
    HouseType.init()
