# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import time
from PIL import Image
import io
import os


USERNAME = "306855276@qq.com"
PASSWORD = "aaaaaaa"
TEMPLATE_PATH = './temp/'


class CookiesWeiboM(object):
    def __init__(self, username, password, browser):
        self.url = "https://passport.weibo.cn/signin/login?entry=mweibo&r=https://m.weibo.cn/"
        self.browser = browser
        self.wait = WebDriverWait(self.browser, 20)
        self.user_name = username
        self.password = password

    def __del__(self):
        self.browser.close()

    def open_login_page(self):
        self.browser.get(self.url)
        user_name = self.wait.until(EC.presence_of_element_located((By.ID, 'loginName')))
        password = self.wait.until(EC.presence_of_element_located((By.ID, 'loginPassword')))
        submit = self.wait.until(EC.presence_of_element_located((By.ID, 'loginAction')))
        print(user_name, password)
        user_name.send_keys(user_name)
        password.send_keys(password)
        submit.click()

    def password_error(self):
        try:
            return WebDriverWait(self.browser, 5).until(
                EC.text_to_be_present_in_element((By.ID, 'errorMsg'), '用户名或密码错误'))
        except TimeoutException:
            return False

    def login_success(self):
        try:
            return bool(
                WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'drop-title'))))
        except TimeoutException:
            return False

    def get_ac_position(self):
        try:
            image = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'patt-shadow')))
            print('发现验证码')
            # time.sleep(2)
            ac_location = image.location
            ac_size = image.size
            ac_top = ac_location['y']
            ac_bottom = ac_location['y'] + ac_size['height']
            ac_left = ac_location['x']
            ac_right = ac_location['x'] + ac_size['width']
            return (ac_top, ac_bottom, ac_left, ac_right)
        except TimeoutException:
            print('未出现验证码')
            # self.open_login_page()
            return None

    def get_page_screenshot(self):
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(io.BytesIO(screenshot))
        return screenshot

    def get_ac_image(self, name='weibo_ac.png'):
        positions = self.get_ac_position()
        if positions == None:
            return None
        top, bottom, left, right = positions
        print('验证码位置: 上({}), 下({}), 左({}), 右({})'.format(top, bottom, left, right))
        page_screenshot = self.get_page_screenshot()
        ac_image = page_screenshot.crop((left, top, right, bottom))
        ac_image.save(name)
        return ac_image

    def get_ac_template(self):
        count = 0
        while True:
            self.open_login_page()
            if self.get_ac_image(str(count) + '.png') is not None:
                count += 1

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        threshold_value = 20
        if abs(pixel1[0] - pixel2[0]) < threshold_value and \
            abs(pixel1[1] - pixel2[1]) < threshold_value and \
            abs(pixel1[2] - pixel2[2]) < threshold_value:
            return True
        else:
            return False

    def is_same_image(self, image, template):
        threshold_value = 0.99
        count = 0
        for x in range(image.width):
            for y in range(image.height):
                if self.is_pixel_equal(image, template. x, y):
                    count += 1
        result = float(count) / (image.width * image.height)
        if result >= threshold_value:
            return True
        else:
            return False

    def detect_ac_image(self, image):
        for template_name in os.listdir(TEMPLATE_PATH):
            print('正在匹配验证码顺序: {}'.format(template_name[0:4]))
            template = Image.open(TEMPLATE_PATH + template_name)
            if self.is_same_image(image, template):
                return list(template_name[0:4])

    def simulate_move(self, numbers):
        points = self.browser.find_element_by_css_selector('.patt-wrap .patt-circ')
        dx = dy = 0
        for index in range(4):
            point = points[numbers[index] - 1]
            if index == 0:
                webdriver.ActionChains(self.browser) \
                .move_to_element_with_offset(point, point.size['width'] / 2, point.size['height'] / 2) \
                .click_and_hold().perform()
            else:
                times = 30
                for i in range(times):
                    webdriver.ActionChains(self.browser).move_by_offset(dx / times, dy / times).perform()
                    time.sleep(1 / times)

            if index == 3:
                webdriver.ActionChains(self.browser).release().perform()
            else:
                dx = points[numbers[index + 1] - 1].location['x'] - points.location['x']
                dy = points[numbers[index + 1] - 1].location['y'] - points.location['y']

    def get_cookies(self):
        return self.browser.get_cookies()

    def start(self):
        self.open_login_page()
        if self.password_error():
            return {
                'status': 2,
                'content': '用户名或密码错误'
            }

        if self.login_success():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }

        image = self.get_ac_image('captcha.png')
        if image == None:
            print('获取验证码失败')
            return None

        numbers = self.detect_ac_image(image)
        self.simulate_move(numbers)
        if self.login_success():
            cookies = self.get_cookies()
            return {
                'status': 1,
                'content': cookies
            }
        else:
            return {
                'status': 3,
                'content': '登录失败'
            }






if __name__ == '__main__':
    weibo = CookiesWeiboM()
    # weibo.get_ac_template()
    weibo.open_login_page()

