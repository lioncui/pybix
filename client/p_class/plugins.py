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


import time
from lib import pybixlib
import threading
import config
import urllib2
import json
import traceback
import re
import random
import base64


class plugin(threading.Thread):

    def __init__(self, uuid, taskConf, agentType):
        self.uuid = uuid
        self.taskConf = taskConf
        self.agentType = agentType
        self.logHead = 'Task_ID:' + uuid + '  Type:' + agentType + '  Error:'
        self.code = 'ok'
        self.error_info = ''
        self.Data = ""
        self.lock = threading.Lock()
        self.running = True
        self.interval = 60
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(random.randint(1, 20))
        while self.running:
            if 'pluginTime' in self.taskConf:
                self.interval = int(self.taskConf['pluginTime'])
            cur_time = time.time()
            self.getData()
            self.postData()
            cur_time = time.time() - cur_time
            if(cur_time < self.interval):
                time.sleep(self.interval - cur_time)
            else:
                pybixlib.error('get data out time!!')
                time.sleep(60)

    def plugStop(self):
        try:
            self.lock.acquire()
            self.running = False
        finally:
            self.lock.release()

    def plugStart(self):
        try:
            self.lock.acquire()
            self.running = True
        finally:
            self.lock.release()

    def errorInfoDone(self, info):
        try:
            self.lock.acquire()
            rem = re.compile(r'(.*)\n', re.M)
            matches = rem.findall(info)
            lens = len(matches)
            if lens > 1:
                self.error_info = matches[0]+matches[1]+'  '+matches[lens-1]
            else:
                self.error_info = info
            self.code = 'error'
        finally:
            self.lock.release()

    def setConf(self, conf):
        try:
            self.lock.acquire()
            self.taskConf = conf
        except Exception:
            pass
        finally:
            self.lock.release()

    def getWebReq(self):
        url = self.taskConf.get('status_url')
        url = url.replace('\/', "/")
        user = self.taskConf.get('user')
        password = self.taskConf.get('password')
        if user and password:
            secret = base64.encodestring("%s:%s" % (user, password))
            secret = secret.replace('\n', '')
            headers = {
                'Authorization': 'Basic %s' % secret
            }
        req = urllib2.Request(url, headers=headers)
        return req

    def getCurTime(self):
        try:
            self.lock.acquire()
            return int(time.time())
        finally:
            self.lock.release()

    def intStatus(self):
        self.code = 'ok'
        self.error_info = ''

    def returnData(self):
        try:
            self.lock.acquire()
            return self.Data
        finally:
            self.lock.release()

    def setData(self, data):
        try:
            self.lock.acquire()
            self.Data = data
        finally:
            self.lock.release()

    def getData(self):
        return {}

    def clearData(self):
        try:
            self.lock.acquire()
            self.Data = ""
        finally:
            self.lock.release()

    def postData(self):
        try:
            reData = {}
            reData[self.uuid+''] = self.returnData()
            self.clearData()
            parms = {'post_data': reData, 'post_time': int(
                self.getCurTime()), 'plug_post': 'true'}
            PostUrl = config.postUrl + "/" + self.uuid
            try:
                req = urllib2.Request(PostUrl)
                req.add_header("Content-Type", "application/json")
                res = urllib2.urlopen(
                    req, json.dumps(parms))
                res.close()
            except Exception:
                pybixlib.error(traceback.format_exc())
                res = urllib2.urlopen(urllib2.Request(PostUrl, parms))
                res.close()

        except Exception:
            pybixlib.error(traceback.format_exc())
