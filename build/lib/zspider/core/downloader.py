import requests
from zspider.http.response import Response

class Downloader():

    def get_response(self,request):
        '''
        实现结构请求对象，发送请求，获取响应
        :param request: 请求对象
        :return: resposne对象
        '''
        if request.method.upper()=="GET":
            ret=requests.get(request.url,headers=request.headers,params=request.params)
        elif request.method.upper()=="POST":
            ret =requests.post(request.url,data=request.data,headers=request.headers,params=request.params)
        else:
            raise Exception("不支持的请求方式<{}>".format(request.method))

        return Response(url=ret.url,headers=ret.headers,status_code=ret.status_code,body=ret.content)