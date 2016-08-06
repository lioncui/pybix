#!/usr/bin/python
# -*- coding: utf-8 -*-


from lib import pybixlib
import traceback
import re
from p_class import plugins
import urllib2


class TomcatPlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)

    def getData(self):
        status_content = {}
        try:
            req = self.getWebReq()
            res = urllib2.urlopen(req)
            data = res.read()
            res.close()
            appname = self.taskConf.get("appname")
            try:
                data = data.decode("UTF8")
            except Exception:
                data = data.decode("GBK")

            rem = re.compile(
                r'<td class="row-center"><small>(.*)</small></td>', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['tomcat_ver'] = matches[0]
                status_content['jvm_ver'] = matches[1]
                status_content['os_ver'] = matches[3]+'  '+matches[4]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data tomcat_ver")
                self.errorInfoDone("can't match the data tomcat_ver")

            rem = re.compile(
                r'Free memory: ([0-9.]*) MB Total memory: ([0-9.]*) MB Max memory: ([0-9.]*) MB</p>', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['free_memory'] = matches[0][0]
                status_content['total_memory'] = matches[0][1]
                status_content['max_memory'] = matches[0][2]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data free_memory")
                self.errorInfoDone("can't match the data free_memory")

            rem = re.compile(r'<h1>([^JVM][^</.]*)</h1>', re.M)
            matches = rem.findall(data)
            flag = -1
            if matches:
                for key, val in enumerate(matches):
                    val = val.strip('"')
                    if val == appname:
                        flag = key
                        break
                if flag == -1:
                    pybixlib.error(
                        self.logHead + "can't find the data appname")
                    self.errorInfoDone("can't find the data appname")
            else:
                pybixlib.error(self.logHead + "can't match the data appname")
                self.errorInfoDone("can't match the data appname")

            status_content['appname'] = appname
            rem = re.compile(r'Max threads: ([0-9]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['max_threads'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data max_threads")
                self.errorInfoDone("can't match the data max_threads")

            rem = re.compile(r'Current thread count: ([0-9]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['cur_thread'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data cur_thread")
                self.errorInfoDone("can't match the data cur_thread")

            rem = re.compile(r'Current thread busy: ([0-9]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['cur_thread_b'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data cur_thread_b")
                self.errorInfoDone("can't match the data cur_thread_b")

            rem = re.compile(r'Max processing time: ([0-9.]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['max_processing_time'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data max_processing_time")
                self.errorInfoDone("can't match the data max_processing_time")

            rem = re.compile(r'Processing time: ([0-9.]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['processing_time'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data processing_time")
                self.errorInfoDone("can't match the data processing_time")

            rem = re.compile(r'Request count: ([0-9.]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['request_count'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data request_count")
                self.errorInfoDone("can't match the data request_count")

            rem = re.compile(r'Error count: ([0-9.]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['error_count'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data error_count")
                self.errorInfoDone("can't match the data error_count")

            rem = re.compile(r'Bytes received: ([0-9.]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['bytes_received'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data bytes_received")
                self.errorInfoDone("can't match the data bytes_received")

            rem = re.compile(r'Bytes sent: ([0-9.]*)[^\d^.]', re.M)
            matches = rem.findall(data)
            if matches:
                status_content['bytes_sent'] = matches[flag]
            else:
                pybixlib.error(
                    self.logHead + "can't match the data bytes_sent")
                self.errorInfoDone("can't match the data bytes_sent")
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            status_content = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': status_content, 'error_info': self.error_info})
            self.intStatus()
