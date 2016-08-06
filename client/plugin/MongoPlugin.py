#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib import pybixlib
import traceback
from p_class import plugins
import pymongo


class MongoPlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)

    def getData(self):
        redata = {}
        try:
            host = self.taskConf.get("host")
            port = self.taskConf.get("port")
            #user = self.taskConf.get("user")
            #password = self.taskConf.get("password")
            engine = pymongo.MongoClient(
                host=host, port=port, document_class=dict, tz_aware=False, connect=True)
            db = engine.test
            data = db.command('serverStatus')

            redata['version'] = data['version']
            redata['host'] = data['host']
            redata['uptime'] = data['uptime']
            if 'ratio' not in data['globalLock']:
                data['globalLock']['ratio'] = 0
            redata['globalLock_ratio'] = data['globalLock']['ratio']
            redata['connections_current'] = data['connections']['current']
            redata['connections_available'] = data['connections']['available']
            redata['page_faults'] = data['extra_info']['page_faults']
            redata['globalLock_currentQueue_total'] = data[
                'globalLock']['currentQueue']['total']
            redata['globalLock_currentQueue_readers'] = data[
                'globalLock']['currentQueue']['readers']
            redata['globalLock_currentQueue_writers'] = data[
                'globalLock']['currentQueue']['writers']
            redata['opcounters_insert'] = data['opcounters']['insert']
            redata['opcounters_query'] = data['opcounters']['query']
            redata['opcounters_update'] = data['opcounters']['update']
            redata['opcounters_delete'] = data['opcounters']['delete']
            redata['opcounters_getmore'] = data['opcounters']['getmore']
            redata['opcounters_command'] = data['opcounters']['command']
            redata['mem_resident'] = data['mem']['resident']
            redata['mem_maped'] = data['mem']['mapped']
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            redata = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': redata, 'error_info': self.error_info})
            self.intStatus()
