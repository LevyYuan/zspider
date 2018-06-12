from lxml import etree
import re


class Response:
    '''完成对响应对象的封装'''
    def __init__(self,url,body,headers,status_code,meta={}):
        '''
        初始化resposne对象
        :param url: 响应的url地址
        :param body: 响应体
        :param headers:  响应头
        :param status_code: 状态码
        '''
        self.url = url
        self.headers=headers
        self.status_code = status_code
        self.body = body
        self.meta=meta

    def xpath(self,rule):
        html=etree.HTML(self.body)
        return html.xpath(rule)

    def re_findall(self, rule, data=None):
        '''封装正则的findall方法'''
        if data is None:
            data = self.body
        return re.findall(rule, data)