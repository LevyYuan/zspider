from .downloader import Downloader
from .pipeline import Pipeline
from .scheduler import Scheduler
from .spider import Spider
from zspider.http.request import Request
from datetime import datetime
from zspider.utils.log import logger
from zspider.middlewares.downloadermiddlewares import Downloadermiddleware
from zspider.middlewares.spidermiddlewares import Spidermiddleware
import time
import importlib
from zspider.conf.settings import SPIDERS, PIPELINES, \
    SPIDER_MIDDLEWARES, DOWNLOADER_MIDDLEWARES


class Engine():
    def __init__(self,spider):
        self.spider=spider
        self.downloader=Downloader()
        self.pipeline =Pipeline()
        self.scheduler= Scheduler()
        self.spidermiddleware=Spidermiddleware()
        self.downloadermiddleware= Downloadermiddleware()
        self.totalrequestnum=0
        self.totalresponsenum=0

        # self.spiders = self._auto_import_instances(SPIDERS, isspider=True)
        #
        # self.pipelines = self._auto_import_instances(PIPELINES)
        # self.spider_mids = self._auto_import_instances(SPIDER_MIDDLEWARES)
        # self.downloader_mids = self._auto_import_instances(DOWNLOADER_MIDDLEWARES)


    def start_engine(self):

        '''
        提供引擎启动的入口
        :return:
        '''
        start_time = datetime.now()
        logger.info("爬虫启动：{}".format(start_time))
        self._start_engine()
        end_time = datetime.now()
        logger.info("爬虫发出的请求：{}".format(str(self.totalrequestnum)))
        logger.info("爬虫获取的响应：{}".format(str(self.totalrequestnum)))
        logger.info("爬虫结束：{}".format(start_time))
        logger.info("爬虫一共运行：{}秒".format((end_time - start_time).total_seconds()))

        pass

    def _start_engine(self):
        # 1.构造spider中start_urls中的请求
        # 2.传递给调取器进行保存，之后从中取出
        # 3.取出的request对象交给下载的进行下载，返回response
        # 4.response交给爬虫模块进行解析，提取结果
        # 5.如果结果是request对象，重新交给调度器，如果结果是item对象，交给管道处理

        self._start_request()

        while True:
            # 避免cpu空转
            time.sleep(0.001)
            self._execute_request_response_item()
            if self.totalresponsenum>=self.totalrequestnum:
                break

    def _execute_request_response_item(self):
        req = self.scheduler.get_request()
        # 下载中间件处理请求
        self.downloadermiddleware.process_request(req)
        # 3.取出的request对象交给下载的进行下载，返回response
        response = self.downloader.get_response(req)

        response.meta=req.meta

        # 下载中间件处理响应
        response = self.downloadermiddleware.process_response(response)
        # 爬虫中间件处理响应
        response = self.spidermiddleware.process_response(response)

        # 因为可能执行的解析数据的函数不一样所以这里不能直接使用parse
        # 需要先获取是哪个函数解析
        parse=getattr(self.spider,req.callback)

        # 4.response交给爬虫模块进行解析，提取结果
        for ret in parse(response):
            # 5.如果结果是request对象，重新交给调度器，如果结果是item对象，交给管道处理
            if isinstance(ret, Request):
                # 爬虫中间件处理请求
                self.spidermiddleware.process_request(ret)
                self.scheduler.add_request(ret)
                self.totalrequestnum+=1
            else:
                self.pipeline.process_item(ret, self.spider)
        self.totalresponsenum+=1

    def _start_request(self):
        # 1.构造spider中start_urls中的请求
        for request in self.spider.start_request():
            # 爬虫中间件处理请求
            self.spidermiddleware.process_request(request)

            # 2.传递给调取器进行保存，之后从中取出
            self.scheduler.add_request(request)
            self.totalrequestnum+=1

    def _auto_import_instances(self, path=[], isspider=False):
        '''通过配置文件，动态导入类并实例化
        path: 表示配置文件中配置的导入类的路径
        isspider: 由于爬虫需要返回的是一个字典，因此对其做对应的判断和处理
        '''
        # 该方法不仅实例化动态导入爬虫，还有管道和中间件，而前者返回应是字典类型
        if isspider is True:
            instances = {}
        else:
            instances = []  # 存储对应类的实例对象

        for p in path:
            module_name = p.rsplit(".", 1)[0]  # 取出模块名称
            cls_name = p.rsplit(".", 1)[1]  # 取出类名称
            ret = importlib.import_module(module_name)  # 动态导入爬虫模块
            cls = getattr(ret, cls_name)  # 根据类名称获取类对象
            if isspider is True:
                instances[cls.name] = cls()
            else:
                instances.append(cls())  # 实例化类对象
        return instances  # 返回类对象