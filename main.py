import sys
import os
from scrapy.cmdline import execute


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 博客园的爬虫执行
# execute(["scrapy", "crawl", "cnblogs"])

# 知乎的爬虫执行
# execute(["scrapy", "crawl", "zhihu"])

# 拉勾的爬虫执行
execute(["scrapy", "crawl", "zhuhu"])