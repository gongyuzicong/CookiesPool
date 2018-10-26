# -*- coding:utf-8 -*-

from login.weibo import cookies
from cookiespool import settings
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from cookiespool import storer
import json

class CookiesGenerator(object):
    def __init__(self, website="undefine"):
        self.website = website
        self.redis_cookies = storer.RedisClient('cookies', self.website)
        self.redis_accounts = storer.RedisClient('accounts', self.website)
        if settings.BROWSER_TYPE == 'PhantomJS':
            caps = DesiredCapabilities.PHANTOMJS
            caps["phantomjs.page.settings.userAgent"] = settings.HEADERS['User-Agent']
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
            self.browser.set_window_size(1400, 500)
        elif settings.BROWSER_TYPE == 'Chrome':
            self.browser = webdriver.Chrome()

    def new_cookies(self, username, password):
        '''定义接口'''
        raise NotImplementedError

    def process_cookies(self, cookies):
        dict = {}
        for cookie in cookies:
            dict[cookie['name']] = cookie['value']
        return dict

    def close_generator(self):
        try:
            print('Closing Browser')
            self.browser.close()
            del self.browser
        except TypeError:
            print('Browser not opened')

    def start(self):
        accounts_usernames = self.redis_accounts.get_all_user_name()
        cookies_usernames = self.redis_cookies.get_all_user_name()

        for username in accounts_usernames:
            if not username in cookies_usernames:
                password = self.redis_accounts.get_value(username)
                print('正在生成Cookies', '账号', username, '密码', password)
                result = self.new_cookies(username, password)
                # 成功获取
                if result.get('status') == 1:
                    cookies = self.process_cookies(result.get('content'))
                    print('成功获取到Cookies', cookies)
                    if self.redis_cookies.set_value(username, json.dumps(cookies)):
                        print('成功保存Cookies')
                # 密码错误，移除账号
                elif result.get('status') == 2:
                    print(result.get('content'))
                    if self.redis_accounts.del_key_value(username):
                        print('成功删除账号')
                else:
                    print(result.get('content'))
        else:
            print('所有账号都已经成功获取Cookies')


class CookiesGeneratorForWeiboM(CookiesGenerator):
    def __init__(self, website='weibo'):
        CookiesGenerator.__init__(self, website)
        self.website = website

    def new_cookies(self, username, password):
        return cookies.CookiesWeiboM(username, password, self.browser).start()

