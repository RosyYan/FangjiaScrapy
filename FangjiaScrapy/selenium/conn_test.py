# -*- coding: utf-8 -*-
"""
@author: yzx
"""

from selenium import webdriver
from scrapy.selector import Selector

# 在chrome中设置不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs)
browser = webdriver.Chrome(executable_path='F:/Download/selenium/chromedriver.exe')

"""
模拟获取动态页面信息
"""


def get_anjuke_page():
    browser.get('https://gz.lianjia.com/ershoufang/')
    print(browser.page_source)
    t_selector = Selector(text=browser.page_source)
    page = t_selector.css('.page-box.house-lst-page-box .on::text').extract()
    print(page)
    browser.quit()


"""
模拟进度条下拉：以开源中国blog为例
"""


def get_dynamic_page():
    browser.get('https://www.oschina.net/blog')
    import time
    time.sleep(5)
    for i in range(3):
        browser.execute_script(
            'window.scrollTo(0,document.body.scrollHeight);var lenOfPage=document.body.scrollHeight; return lenOfPage;')
        time.sleep(3)
    browser.quit()


if __name__ == '__main__':
    browser.get('https://www.taobao.com')
    print(browser.page_source)
    browser.quit()
