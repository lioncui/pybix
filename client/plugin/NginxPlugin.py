#!/usr/bin/python
# -*- coding: utf-8 -*-


from lib import pybixlib
import traceback
import re
from p_class import plugins
import urllib2
import codecs


class NginxPlugin(plugins.plugin):

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
            rem = re.compile(r'Active connections: ([0-9]*)', re.M)
            matches = rem.findall(data)
            if matches:
                curr_reqs = matches[0]
            else:
                pybixlib.error(
                    self.logHead + ' data format:Active connections')
                return

            rem = re.compile(r' ([0-9]*) ([0-9]*) ([0-9]*) ', re.M)
            matches = rem.findall(data)
            if matches:
                accepts = matches[0][0]
                handled = matches[0][1]
                requests = matches[0][2]
            else:
                pybixlib.error(self.logHead + ' data format:num')
                return

            rem = re.compile(r'Reading: ([0-9]*)', re.M)
            matches = rem.findall(data)
            if matches:
                reading = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:Reading')
                return

            rem = re.compile(r'Writing: ([0-9]*)', re.M)
            matches = rem.findall(data)
            if matches:
                writing = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:Writing')
                return

            rem = re.compile(r'Waiting: ([0-9]*)', re.M)
            matches = rem.findall(data)
            if matches:
                waiting = matches[0]
            else:
                pybixlib.error(self.logHead + ' data format:Waiting')
                return

            redata = {'curr_reqs': curr_reqs, 'reading': reading, 'writing': writing,
                      'waiting': waiting, 'accepts': accepts, 'handled': handled, 'requests': requests}

        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': redata, 'error_info': self.error_info})
            self.intStatus()
