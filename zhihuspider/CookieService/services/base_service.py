import abc


# 元类编程
class BaseService(metaclass=abc.ABCMeta):
    """cookie管理模块的抽象基类，主要包括了登录和检查cookie这两个抽象方法
    """

    @abc.abstractclassmethod
    def login(self):
        pass

    @abc.abstractclassmethod
    def check_cookie(self, cookie_dict):
        pass
