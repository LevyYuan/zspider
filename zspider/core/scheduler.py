from six.moves.queue import Queue
from hashlib import sha1
import w3lib.url
import six

class Scheduler():
    '''完成调取器模块的封装'''
    def __init__(self):
        self.queue=Queue()
        self._filter_container = set()

    def add_request(self,request):
        '''
        实现添加request到队列中
        :param request: 请求对象
        :return: None
        '''
        # url去重
        # self._filter_request(request)
        self.queue.put(request)

    def get_request(self):
        '''
        实现获取队列中的request对象
        :return: 请求对象
        '''
        return self.queue.get()

    def _filter_request(self,request):
        '''
        实现对请求对象的去重
        :param request: 请求对象
        :return: bool
        '''
        # 去重容器：存储已经发过的请求的特征 url    选用集合类型：set()
        # 利用请求的url method data  求出一个指纹  利用sha1
        request.fp = self._gen_fp(request)
        if request.fp not in self._filter_container:
            self._filter_container.add(request.fp)
            # logger.info("添加新的请求：<%s>" % request.url)
            return True
        else:
            # logger.info("发现重复的请求：<%s>" % request.url)
            self.repeate_request_num += 1
            return False

    def _gen_fp(self, request):
        '''请求去重，计算指纹'''
        # 用来判断请求是否重复的属性：url，method，params，data
        # 为保持唯一性，需要对他们按照同样的排序规则进行排序
        # 1. url排序：借助w3lib.url模块中的canonicalize_url方法
        url = w3lib.url.canonicalize_url(request.url)
        # 2. method不需要排序，只要保持大小写一致就可以
        method = request.method.upper()
        # 4. data排序：如果有提供则是一个字典，如果没有则是空字典
        data = request.data if request.data is not None else {}
        data = sorted(data.items(), key=lambda x: x[0])

        # 5. 利用sha1算法，计算指纹
        s1 = sha1()
        # 为了兼容py2和py3，利用_to_bytes方法，把所有的字符串转化为字节类型
        s1.update(self._to_bytes(url))
        s1.update(self._to_bytes(method))
        s1.update(self._to_bytes(str(data)))

        fp = s1.hexdigest()
        return fp

    @staticmethod
    def _to_bytes(string):
        if six.PY2:
            if isinstance(string, str):
                return string
            else:  # 如果是python2的unicode类型，转化为字节类型
                return string.encode("utf-8")
        elif six.PY3:
            if isinstance(string, str):  # 如果是python3的str类型，转化为字节类型
                return string.encode("utf-8")
            else:
                return string