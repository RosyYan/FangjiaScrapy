# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
from fake_useragent import UserAgent

from utils.crawl_ip import GetIP


class FangjiascrapySpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class FangjiascrapyDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class my_proxy(object):
    def process_request(self, request, spider):
        pass


class my_useragent(object):
    def process_request(self, request, spider):
        USER_AGENT_LIST = [
            'MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23',
            'Opera/9.20 (Macintosh; Intel Mac OS X; U; en)',
            'Opera/9.0 (Macintosh; PPC Mac OS X; U; en)',
            'iTunes/9.0.3 (Macintosh; U; Intel Mac OS X 10_6_2; en-ca)',
            'Mozilla/4.76 [en_jp] (X11; U; SunOS 5.8 sun4u)',
            'iTunes/4.2 (Macintosh; U; PPC Mac OS X 10.2)',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:5.0) Gecko/20100101 Firefox/5.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:9.0) Gecko/20100101 Firefox/9.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:16.0) Gecko/20120813 Firefox/16.0',
            'Mozilla/4.77 [en] (X11; I; IRIX;64 6.5 IP30)',
            'Mozilla/4.8 [en] (X11; U; SunOS; 5.7 sun4u)'
        ]
        agent = random.choice(USER_AGENT_LIST)
        request.headers['User_Agent'] = agent


class RandomUserAgentMiddleware(object):
    # 随机更换user-agent
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault('User-Agent', get_ua())


class RandomProxyMiddleware(object):
    # 动态设置ip代理
    def process_request(self, request, spider):
        get_ip = GetIP()
        request.meta["proxy"] = get_ip.get_random_ip()


from scrapy.http import HtmlResponse
from scrapy.selector import Selector
from PIL import Image, ImageEnhance
import pytesseract


class JSPageMiddleware(object):
    def process_request(self, request, spider):
        # 通过chrome访问安居客
        if spider.name == 'anjuke':
            spider.browser.get(request.url)
            spider.browser.implicitly_wait(1)
            print('安居客:{0}'.format(request.url))
            # 防止重复请求:scrapy直接返回给spider,不会发送给Downloader
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8',
                                request=request)
        elif spider.name == 'lianjia':
            spider.browser.get(request.url)
            spider.browser.implicitly_wait(2)
            print('链家:{0}'.format(request.url))
            # 防止重复请求:scrapy直接返回给spider,不会发送给Downloader
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8',
                                request=request)

        # 解决阳光家缘、房天下的验证码识别问题
        elif spider.name == 'jiayuan':
            return self.handle_jiayuan(request, spider)

        elif spider.name == 'fangtianxia':
            return self.handle_fang(request, spider)

    def handle_fang(self, request, spider):
        screenImg = 'F:/FangjiaScrapy/FangjiaScrapy/utils/images/fang_captcha.png'
        spider.browser.get(request.url)
        spider.browser.implicitly_wait(10)
        print('房天下：%s' % request.url)
        selector = Selector(text=spider.browser.page_source)
        verify_info = selector.css('div.verify_info')
        while verify_info:
            print('验证码问题...')
            spider.browser.save_screenshot(screenImg)
            img = Image.open(screenImg).crop(())
            img = img.convert('L')
            img = ImageEnhance.Contrast(img).enhance(2.0)
            img.save(screenImg)
            code = pytesseract.image_to_string(img)
            spider.browser.find_element_by_css_selector("input#code").send_keys(code)
            spider.browser.find_element_by_xpath(
                '//div[@id="verify_page"]//form/div[@class="button"]/input').click()
            spider.browser.implicitly_wait(3)
            selector = Selector(text=spider.browser.page_source)
            verify_info = selector.css('div.verify_info')
            if not verify_info:
                break
        return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8',
                            request=request)

    def handle_jiayuan(self, request, spider):
        screenImg = 'F:/FangjiaScrapy/FangjiaScrapy/utils/images/jiayuan_captcha.png'
        spider.browser.get(request.url)
        spider.browser.implicitly_wait(2)
        print('阳光家缘:{0}'.format(request.url))
        selector = Selector(text=spider.browser.page_source)
        #  handle the error or invalid verification code
        err_text = selector.css(".MS dd li::text").extract_first()
        #  handle the normal page
        normal_text = selector.css("div.resultList")
        if not err_text:
            if normal_text:
                spider.browser.implicitly_wait(2)
                return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source,
                                    encoding='utf-8', request=request)
            self.jiayuan_handler(spider.browser, screenImg)
        while err_text and '验证码错误' in err_text:
            spider.browser.find_element_by_css_selector("a#LnkReturnUrl").click()
            spider.browser.implicitly_wait(3)
            self.jiayuan_handler(spider.browser, screenImg)
            selector = Selector(text=spider.browser.page_source)
            err_text = selector.css(".MS dd li::text").extract_first()
            if not err_text:
                break

        # 防止重复请求:scrapy直接返回给spider,不会发送给Downloader
        # print(spider.browser.current_url)
        return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding='utf-8',
                            request=request)

    def jiayuan_handler(self, browser, img_src):
        browser.execute_script(
            'window.scrollTo(0,document.body.scrollHeight); var lenOfPage = document.body.scrollHeight; return lenOfPage;')
        # 滑动到底部后截屏
        browser.save_screenshot(img_src)
        img = Image.open(img_src).crop((683, 366, 753, 386))
        img = img.convert('L')
        img = ImageEnhance.Contrast(img).enhance(2.0)
        img.save(img_src)
        img = Image.open(img_src)
        code = pytesseract.image_to_string(img)
        browser.find_element_by_id('ValidateCode').send_keys(code)
        browser.find_element_by_css_selector('input.submit').click()
        browser.implicitly_wait(3)
