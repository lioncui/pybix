#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from lib import pybixlib
import traceback
from p_class import plugins
import re
import codecs
import urllib2


class ApachePlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)

    def strtotime(self, strtime):
        try:
            time_tuple = time.strptime(strtime, "%d-%b-%Y %H:%M:%S")
            timestamp = time.mktime(time_tuple)
            return timestamp
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            return

    def getData(self):
        redata = {}
        try:
            req = self.getWebReq()
            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            try:
                data = data.decode("UTF8")
            except Exception:
                data = data.decode("GBK")
            data = data.replace(codecs.BOM_UTF8.decode("UTF8"), "")
            rem = re.compile(
                r'<dt>Current Time: [a-zA-Z]*, (.*) [^0-9]*</dt>', re.M)
            matches = rem.findall(data)
            if matches:
                curr_time = self.strtotime(matches[0])
            else:
                pybixlib.error(self.logHead + ' data format:Current Time')
                return

            rem = re.compile(
                r'<dt>Restart Time: [a-zA-Z]*, (.*) [^0-9]*</dt>', re.M)
            matches = rem.findall(data)
            if matches:
                restart_time = self.strtotime(matches[0])
            else:
                pybixlib.error(self.logHead + ' data format:Restart Time')
                return
            uptime = curr_time - restart_time

            rem = re.compile(
                r'([0-9]*) requests currently being processed', re.M)
            matches = rem.findall(data)
            if matches:
                curr_reqs = matches[0]
            else:
                pybixlib.error(
                    self.logHead + ' data format:requests currently')
                return

            rem = re.compile(r'<dt>Total accesses: ([0-9]*) -', re.M)
            matches = rem.findall(data)
            if matches:
                total_reqs = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:Total accesses')
                return

            rem = re.compile(r'<pre>(.*)</pre>', re.S)
            matches = rem.findall(data)
            if matches:
                statusStr = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:pre')
                return

            lens = len(statusStr)
            curr_reqs_status = {}
            for i in range(0, lens):
                tmp = statusStr[i]
                if tmp == "\n":
                    continue
                if tmp in curr_reqs_status:
                    curr_reqs_status[tmp] += 1
                else:
                    curr_reqs_status[tmp] = 1

            redata = {'uptime': uptime, 'total_reqs': total_reqs,
                      'curr_reqs': curr_reqs, 'curr_reqs_status': curr_reqs_status}

        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            redata = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': redata, 'error_info': self.error_info})
            self.intStatus()
