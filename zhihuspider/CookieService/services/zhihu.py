"""知乎的cookie登陆服务,当前仅能支持英文验证码识别，而且在登录次数过多的情况下会导致无法登录知乎
"""
import time
import base64

import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from zhihuspider.zhihuspider.CookieService.services.base_service import BaseService
from zhihuspider.zhihuspider.CookieService.common.chaojiying import Chaojiying_Client


class ZhihuLoginService(BaseService):
    name = "zhihu"

    def __init__(self, setting):
        """
        实例初始化，主要是获取一些账户信息，同时打开浏览器操作对象
        :param setting: 配置文件的信息
        """
        self.user_name = setting.Accounts[self.name]["username"]
        self.pass_word = setting.Accounts[self.name]["password"]
        self.setting = setting
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(options=chrome_options)

    def _check_login(self):
        """在页面上查看能否获取某个登录之后才能得到的元素
        """
        try:
            self.browser.find_element_by_xpath('//*[@id="Popover14-toggle"]/img')
            print("已经成功登录")
            return True
        except Exception as e:
            return False

    def check_cookie(self, cookie_dict: dict) -> bool:
        """
        发送http请求检查cookie是否可用
        :return: True: cookie可用, False: cookie不可用
        """
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"}
        res = requests.get("https://www.zhihu.com", headers=headers, cookies=cookie_dict, allow_redirects=False)
        if res.status_code != 200:
            return False
        else:
            return True

    def login(self) -> dict:
        """
        登录知乎
        :return:
        """
        try:
            self.browser.maximize_window()  # 将窗口最大化防止定位错误
        except Exception as e:
            pass

        while not self._check_login():
            self.browser.get("https://www.zhihu.com/signin")

            # 选择密码登录并且点击登录
            time.sleep(5)
            self.browser.find_element_by_xpath('//*[@id="root"]/div/main/div/div/div/div[1]/div/form/div[1]/div[2]').click()

            browser_navigation_panel_height = self.browser.execute_script("return window.outerHeight - "
                                                                          "window.innerHeight;")
            time.sleep(3)

            # 输入用户名和密码
            username_ele = self.browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input")
            username_ele.send_keys(Keys.CONTROL + 'a')
            username_ele.send_keys(self.user_name)
            password_ele = self.browser.find_element_by_css_selector(".SignFlow-password input")
            password_ele.send_keys(Keys.CONTROL + 'a')
            password_ele.send_keys(self.pass_word)
            time.sleep(3)
            self.browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
            time.sleep(5)

            from mouse import move, click
            print("判断是否登录成功")
            if self._check_login():
                break
            try:
                # 查询是否有英文验证码
                english_captcha_ele = self.browser.find_element_by_class_name("Captcha-englishImg")
            except:
                english_captcha_ele = None
            try:
                chinese_captcha_ele = self.browser.find_element_by_class_name("Captcha-chineseImg")
            except:
                chinese_captcha_ele = None

            if chinese_captcha_ele:

                # 获取中文图片标签的绝对坐标
                y_relative_coord = chinese_captcha_ele.location['y']
                y_absolute_coord = y_relative_coord + browser_navigation_panel_height
                x_absolute_coord = chinese_captcha_ele.location['x']
                """
                保存图片
                1. 通过保存base64编码
                2. 通过crop方法
                """
                # 1. 通过保存base64编码
                base64_text = chinese_captcha_ele.get_attribute("src")
                code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                # print code
                fh = open("yzm_cn.jpeg", "wb")
                fh.write(base64.b64decode(code))
                fh.close()

                from zhihuspider.zhihuspider.CookieService.zheye import zheye
                z = zheye()
                positions = z.Recognize("yzm_cn.jpeg")

                pos_arr = []
                if len(positions) == 2:
                    if positions[0][1] > positions[1][1]:
                        pos_arr.append([positions[1][1], positions[1][0]])
                        pos_arr.append([positions[0][1], positions[0][0]])
                    else:
                        pos_arr.append([positions[0][1], positions[0][0]])
                        pos_arr.append([positions[1][1], positions[1][0]])
                else:
                    pos_arr.append([positions[0][1], positions[0][0]])

                if len(positions) == 2:
                    first_point = [int(pos_arr[0][0] / 2), int(pos_arr[0][1] / 2)]
                    second_point = [int(pos_arr[1][0] / 2), int(pos_arr[1][1] / 2)]

                    move((x_absolute_coord + first_point[0]), y_absolute_coord + first_point[1])
                    click()

                    move((x_absolute_coord + second_point[0]), y_absolute_coord + second_point[1])
                    click()

                else:
                    first_point = [int(pos_arr[0][0] / 2), int(pos_arr[0][1] / 2)]

                    move((x_absolute_coord + first_point[0]), y_absolute_coord + first_point[1])
                    click()
                self.browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()

            if english_captcha_ele:
                # 在图片验证码是英文的情况下使用超级鹰打码平台进行识别
                base64_text = english_captcha_ele.get_attribute("src")
                code = base64_text.replace('data:image/jpg;base64,', '').replace("%0A", "")
                with open("yzm_en.jpeg", "wb") as f:
                    f.write(base64.b64decode(code))
                # 使用超级鹰来获取验证码信息
                chaojiying = Chaojiying_Client(self.setting.CJY_USERNAME, self.setting.CJY_PASSWORD, "906264")
                im = open("yzm_en.jpeg", 'rb').read()
                json_data = chaojiying.PostPic(im)
                if json_data["err_no"] == 0:
                    print("识别成功")
                    code = json_data["pic_str"]
                    print("英文验证是：" + code)
                else:
                    print("识别失败, 请继续尝试")
                    return None
                time.sleep(2)
                self.browser.find_element_by_name('captcha').send_keys(code)
                time.sleep(2)
                username_ele = self.browser.find_element_by_css_selector(".SignFlow-accountInput.Input-wrapper input")
                username_ele.send_keys(Keys.CONTROL + 'a')
                username_ele.send_keys(self.user_name)
                password_ele = self.browser.find_element_by_css_selector(".SignFlow-password input")
                password_ele.send_keys(Keys.CONTROL + 'a')
                password_ele.send_keys(self.pass_word)
                time.sleep(3)
                self.browser.find_element_by_css_selector(".Button.SignFlow-submitButton").click()
                time.sleep(5)

        # 获取当前页面的cookies, 并且将其写入到字典之中s
        cookies = self.browser.get_cookies()
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie["name"]] = cookie["value"]
        # self.browser.close()
        print(cookie_dict)
        return cookie_dict


if __name__ == "__main__":
    from zhihuspider.zhihuspider.CookieService import setting
    zhihu_service = ZhihuLoginService(setting)
    zhihu_service.login()
