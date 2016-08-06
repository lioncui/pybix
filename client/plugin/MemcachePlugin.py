#!/usr/bin/python
# -*- coding:utf-8 -*-

from lib import pybixlib
import traceback
from p_class import plugins
from pymemcache.client.base import Client


class MemcachePlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)

    def data_format_MB(self, data):
        data = int(data)
        data = data/1048576
        data = "%.2f" % data
        data = float(data)
        return data

    def data_format_Ratio(self, hit, mis):
        hit = int(hit)
        mis = int(mis)
        if (hit + mis) == 0:
            return 0
        data = (hit*100)/(hit+mis)
        data = "%.2f" % data
        data = float(data)
        return data

    def getData(self):
        status_content = {}
        try:
            host = self.taskConf.get("host")
            port = self.taskConf.get("port")
            mc = Client((host, port))
            status_content = mc.stats()

        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            status_content = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': status_content, 'error_info': self.error_info})
            self.intStatus()
