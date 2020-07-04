# 超级鹰配置
CJY_USERNAME = "huqingsong"
CJY_PASSWORD = "19964312a"

# redis相关信息
REDIS_HOST = "119.3.185.42"
REDIS_PASSWORD = "123"

# 登录知乎 bilibli等网站的信息,cookie是放在redis之中的
Accounts = {
    "zhihu": {
        "username": "18723468514",
        "password": "199643",
        "cookie_key": "zhihu:cookies",
        "max_cookie_nums": 1,
        "check_interval": 30
    },
}