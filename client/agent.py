'''
    Copyright (C) 2016 Lion Cui <lioncui@163.com>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib import pybixlib
import time
import socket
import config
import threading
import traceback
import urllib2
import json

# proxy
try:
    if config.useProxy:
        proxy_handler = urllib2.ProxyHandler(
            {'http': str(config.proxy_host)+':'+str(config.proxy_port)})
        proxy_opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(proxy_opener)
except Exception:
    pass


class AgentProcess(threading.Thread):

    def __init__(self):
        self.running = True
        self.mac = pybixlib.get_mac_address()
        self.ipList = pybixlib.get_ipList()
        self.hostname = pybixlib.get_hostname()
        self.conf = self.getConf()
        self.conf_interval = 120  # 两分钟更新配置
        threading.Thread.__init__(self)
        socket.setdefaulttimeout(30)

    def __del__(self):
        pass

    def stop(self):
        self.running = False

    # Agent主线程
    def run(self):
        self.objList = {}
        try:
            if 'tasks' in self.conf:
                for uuid in self.conf['tasks']:
                    plug = self.conf['tasks'][uuid+'']
                    if plug['status'] == 1:
                        self.startOne(plug)
            else:
                pybixlib.info('none tasks info!!')
            while self.running:
                time.sleep(self.conf_interval)
                conf = self.getConf()
                self.initPlugin(conf)
        except Exception:
            self.stop()
            print traceback.format_exc()
            pybixlib.error(traceback.format_exc())

    # 判断主机是否已被纪录
    def check_host(self):
        try:
            hostUrl = config.hostUrl + "/" + self.mac
            req = urllib2.Request(hostUrl)
            req.add_header("Content-Type", "application/json")
            res = urllib2.urlopen(req)
            res.close()
            return True
        except Exception:
            pybixlib.error(traceback.format_exc())
            pybixlib.error(
                "Please use method 'POST /hosts' to add the host record.")
            return False

    # 重新初始化插件
    def initPlugin(self, conf):
        try:
            if 'tasks' in conf:
                for plugOne in self.objList:
                    if plugOne in conf['tasks']:
                        if 'taskConf' in conf['tasks'][plugOne]:
                            self.objList[plugOne].setConf(
                                conf['tasks'][plugOne]['taskConf'])

                for uuid in conf['tasks']:
                    plug = conf['tasks'][uuid+'']
                    if plug['status'] == '1' and plug['uuid'] not in self.objList:
                        self.startOne(plug)

                    if plug['status'] == '0' and plug['uuid'] in self.objList:
                        self.stopOne(plug)
                    if plug['status'] == '2' and plug['uuid'] in self.objList:
                        self.stopOne(plug)
                        self.startOne(plug)
        except Exception:
            pybixlib.error(traceback.format_exc())

    # 启动插件
    def startOne(self, plug):
        try:
            module_meta = __import__(
                'plugin', globals(), locals(), [str(plug['pluginFileName'])])
            class_meta = getattr(module_meta, plug['pluginFileName'])
            c = getattr(class_meta, plug['pluginClassName'])
            obj = c(plug['uuid'], plug['taskConf'],
                    plug['agentType'])
            self.objList[plug['uuid']] = obj
            obj.setName(plug['pluginClassName']+plug['uuid'])
            obj.setDaemon(True)
            obj.start()
        except Exception:
            pybixlib.error(traceback.format_exc())

    # 停止插件
    def stopOne(self, plug):
        try:
            self.objList[plug['uuid']].plugStop()
            del self.objList[plug['uuid']]
        except Exception:
            pybixlib.error(traceback.format_exc())

    # 获取配置
    def getConf(self):
        if self.check_host():
            try:
                mac_adress = self.mac
                url = config.configUrl + "/" + str(mac_adress)
                req = urllib2.Request(
                    url, headers={"Content-Type": "application/json"})
                res = urllib2.urlopen(req)
                redata = res.read().decode('UTF8')
                res.close()
                return json.loads(redata)
            except Exception:
                pybixlib.error(traceback.format_exc())
        else:
            return {}

if __name__ == "__main__":
    pybixlib.info('Starting agent process')
    pybixlib.printout('Starting agent process')
    try:
        agentProcess = AgentProcess()
        agentProcess.setName('AgentProcess')
        agentProcess.start()
    except Exception:
        pybixlib.error(traceback.format_exc())
