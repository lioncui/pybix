#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib import pybixlib
import traceback
import codecs
from p_class import plugins
import urllib2
import re


class LighttpdPlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)

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
            rem = re.compile(r'<h1>Server-Status(.*)<h2>Connections', re.S)
            matches = rem.findall(data)
            if matches:
                status_content = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:Server-Status')
                return

            rem = re.compile(
                r'Requests<\/td><td class="string">([0-9 ]*)req\/s<\/td>', re.S)
            matches = rem.findall(status_content)
            if matches:
                rps = matches[1]
                rps = int(rps)
            else:
                pybixlib.error(self.logHead + ' data format:Requests')
                return

            rem = re.compile(r'<b>([0-9 ]*)connections', re.S)
            matches = rem.findall(status_content)
            if matches:
                curr_reqs = matches[0]
                curr_reqs = int(curr_reqs)
            else:
                pybixlib.error(self.logHead + ' data format:connections')
                return

            rem = re.compile(r'connections<\/b>(.*)<\/pre><hr', re.S)
            matches = rem.findall(status_content)
            if matches:
                statusStr = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:connections pre')
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

            redata = {'rps': rps, 'curr_reqs': curr_reqs,
                      'curr_reqs_status': curr_reqs_status}
            for key in curr_reqs_status:
                redata['s_'+key] = curr_reqs_status[key]

        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            redata = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': redata, 'error_info': self.error_info})
            self.intStatus()
