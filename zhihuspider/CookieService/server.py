"""
#1. cookie保存在redis中应该使用什么数据结构
#2. 数据结构应该满足： 1. 可以随机获取 2. 可以防止重复 - set
"""
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial

import redis


class CookieServer(object):
    def __init__(self, setting):
        self.redis_cli = redis.Redis(host=setting.REDIS_HOST, password=setting.REDIS_PASSWORD, decode_responses=True)
        self.server_list = []
        self.setting = setting

    def register(self, cls):
        self.server_list.append(cls)

    def login_service(self, srv):
        """
        执行登录获取cookie
        :param srv:
        :return:
        """
        while True:
            srv_cli = srv(self.setting)
            srv_name = srv_cli.name
            cookie_nums = self.redis_cli.scard(self.setting.Accounts[srv_name]["cookie_key"])
            if cookie_nums < self.setting.Accounts[srv_name]["max_cookie_nums"]:
                cookie_dict = srv_cli.login()
                self.redis_cli.sadd(self.setting.Accounts[srv_name]["cookie_key"], json.dumps(cookie_dict))
            else:
                print(srv_name + "的cookie池已满，等待10s")
                time.sleep(10)

    def check_cookie_service(self, srv):
        """
        检查服务的cookie是否可用，不可用的进行清除
        :param srv:
        :return:
        """
        while True:
            print("开始检测cookie是否可用")
            srv_cli = srv(self.setting)
            srv_name = srv_cli.name
            cookie_name = self.setting.Accounts[srv_name]["cookie_key"]
            all_cookies = self.redis_cli.smembers(cookie_name)
            print("目前可以使用的cookie数量是{}".format(len(all_cookies)))
            for cookie in all_cookies:
                print("获取到cookie:{}".format(cookie))
                cookie_dict = json.loads(cookie)
                if srv_cli.check_cookie(cookie_dict):
                    print("cookie有效")
                else:
                    print("cookie已经失效,删除cookie")
                    self.redis_cli.srem(cookie_name, cookie)
            # 设置检测间隔，防止请求过于频繁，导致原本没有失效的cookie失效了
            interval = self.setting.Accounts[srv_name]["check_interval"]
            print("{}秒之后开始重新检测cookie".format(interval))

    def start(self):
        """
        执行利用线程池去执行上面登录和检测任务
        :return:
        """
        task_list = []

        print("启动登录服务")
        login_executor = ThreadPoolExecutor(max_workers=5)
        for srv in self.server_list:
            task = login_executor.submit(partial(self.login_service, srv))
            task_list.append(task)

        print("启动cookie检测服务")
        check_executor = ThreadPoolExecutor(max_workers=5)
        for srv in self.server_list:
            task = check_executor.submit(partial(self.check_cookie_service, srv))
            task_list.append(task)

        for future in as_completed(task_list):
            data = future.result()
            print(data)
