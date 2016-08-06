#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib import pybixlib
import traceback
from p_class import plugins
import redis


class RedisPlugin(plugins.plugin):

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
        if (hit+mis) == 0:
            return 0
        data = (hit*100)/(hit+mis)
        data = "%.2f" % data
        data = float(data)
        return data

    def data_format_connected_per_min(self, connected, min):
        data = float(connected)/min
        data = "%.2f" % data
        return data

    def data_format_command_per_min(self, command, min):
        data = float(command)/min
        data = "%.2f" % data
        return data

    def getData(self):
        status_content = {}
        try:
            host = self.taskConf.get("host")
            port = self.taskConf.get("port")
            password = self.taskConf.get("password")
            self.server = redis.StrictRedis(host=host, port=port,
                                            password=password,
                                            socket_connect_timeout=30)
            self.info = self.server.info()
            status_content['redis_version'] = self.info['redis_version']
            status_content['used_memory'] = self.info['used_memory']
            status_content['connected_clients'] = self.info[
                'connected_clients']
            status_content['connected_slaves'] = self.info['connected_slaves']
            status_content['uptime_in_minutes'] = self.info[
                'uptime_in_seconds'] / 60
            #status_content['connected_per_min'] = self.data_format_connected_per_min(status_content['connected_clients'], status_content['uptime_in_minutes'])
            status_content['rejected_connections'] = self.info[
                'rejected_connections']
            status_content['pubsub_patterns'] = self.info['pubsub_patterns']
            status_content['pubsub_channels'] = self.info['pubsub_channels']
            status_content['keyspace_hits'] = self.info['keyspace_hits']
            status_content['keyspace_misses'] = self.info['keyspace_misses']
            #status_content['keyspace_hits'] = self.data_format_Ratio(self.info['keyspace_hits'], self.info['keyspace_misses'])
            status_content['commands_total'] = self.info[
                'total_commands_processed']
            #status_content['command_per_min'] = self.data_format_command_per_min(self.info['total_commands_processed'], status_content['uptime_in_minutes'])
            status_content['usedMemoryRss'] = self.info['used_memory_rss']
            status_content['memFragmentationRatio'] = self.info[
                'mem_fragmentation_ratio']
            status_content['blockedClients'] = self.info['blocked_clients']
            totalKey = 0
            for key in self.info:
                if key.startswith('db'):
                    totalKey = totalKey + self.info[key]['keys']
            status_content['totalKeys'] = totalKey
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            status_content = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': status_content, 'error_info': self.error_info})
            self.intStatus()
