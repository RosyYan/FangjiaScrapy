# -*- coding: utf-8 -*-
"""
@author: yzx
"""

from scrapy.cmdline import execute
import sys
import os

if __name__ == '__main__':
    """
    到项目工程目录下才能执行execute方法来执行scrapy命令:scrapy crawl lianjia
    'lianjia' 必须和spiders中的name值一致
    可以在spiders中打断点
    """

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(['scrapy', 'crawl', 'lianjia'])
    # execute(['scrapy', 'crawl', 'fangtianxia'])
    # execute(['scrapy', 'crawl', 'anjuke'])


