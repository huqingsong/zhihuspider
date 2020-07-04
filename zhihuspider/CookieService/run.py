from zhihuspider.zhihuspider.CookieService.server import CookieServer
from zhihuspider.zhihuspider.CookieService.services.zhihu import ZhihuLoginService

from zhihuspider.zhihuspider.CookieService import setting

if __name__ == "__main__":
    srv = CookieServer(setting)
    srv.register(ZhihuLoginService)

    # 启动cookie池服务
    srv.start()
