# encoding=utf8
from urllib import request, parse


class SpiderBase(object):
    content = ""

    def __init__(self, url):
        # 添加请求头，模仿浏览器
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/6.0')
        response = request.urlopen(req)
        self.content=response.read()


