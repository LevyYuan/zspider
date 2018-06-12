

class Request():
    def __init__(self,url,method="GET",params=None,headers=None,data=None,callback="parse",meta=None):
        '''
        初始化request对象
        :param url: url地址
        :param method: 请求方法
        :param headers: 请求头
        :param params: 请求的参数
        :param data: 请求体
        '''
        self.url=url
        self.method=method
        self.params=params
        self.headers=headers
        self.data=data
        self.callback=callback
        self.meta=meta