#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib import pybixlib
import traceback
from p_class import plugins
import time
import psutil


class ServerPlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)
        self.oldNetSentValue = {}
        self.oldNetRecvValue = {}
        #self.option = {1: max, 2: min}
        self.ip = {}
        self.get_ip()

    def get_ip(self):
        netifaddrs = psutil.net_if_addrs()
        for interface in netifaddrs:
            if interface == '':
                continue
            for snic in netifaddrs[interface]:
                if str(snic.family) == '2':
                    if len(snic.address) > 7:
                        self.ip[interface] = snic.address

    def data_format_KB(self, data):
        data = int(data)
        data = data/1024
        data = "%.2f" % data
        data = float(data)
        return data

    def data_format_MB(self, data):
        data = int(data)
        data = data/1024/1024
        data = "%.2f" % data
        data = float(data)
        return data

    def data_format_GB(self, data):
        data = int(data)
        data = data/1024/1024/1024
        data = "%.2f" % data
        data = float(data)
        return data

    def data_format_Ratio(self, hit, total):
        hit = int(hit)
        total = int(total)
        if total == 0:
            return 0
        data = (hit*100)/total
        data = "%.2f" % data
        data = float(data)
        return data

    def get_mem_info(self):
        returnData = {}
        try:
            mem = psutil.virtual_memory()
            returnData['phymem_used'] = self.data_format_KB(mem.used)
            returnData['phymem_free'] = self.data_format_KB(mem.free)
            returnData['phymem_percent'] = mem.percent
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())

        return returnData

    def get_cpu_info(self):
        returnData = {}
        try:
            cpu = psutil.cpu_percent(interval=5, percpu=False)
            returnData['cpu_percent'] = cpu
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def get_disk_io_info(self):
        returnData = {'readiokps': {}, 'writeiokps': {}}
        try:
            old_info = psutil.disk_io_counters(perdisk=True)
            time.sleep(1)
            new_info = psutil.disk_io_counters(perdisk=True)
            for (diskname, rwinfo) in old_info.items():
                oldr, oldw = rwinfo.read_bytes, rwinfo.write_bytes
                newr, neww = new_info[diskname].read_bytes, new_info[
                    diskname].write_bytes
                riok = (newr - oldr) / 1024.0
                wiok = (neww - oldw) / 1024.0
                returnData['readiokps'][diskname] = riok
                returnData['writeiokps'][diskname] = wiok
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def get_disk_rate_info(self):
        returnData = {}
        returnData['disk_total'] = {}
        returnData['disk_used'] = {}
        returnData['disk_percent'] = {}
        try:
            disk = psutil.disk_partitions()
            for val in disk:
                if val.fstype != "":
                    mountpoint = val.mountpoint
                    one = psutil.disk_usage(mountpoint)
                    tmp = one.total/1024/1024/1024.0
                    returnData['disk_total'][mountpoint] = "%.2f" % tmp
                    tmp = one.used/1024/1024/1024.0
                    returnData['disk_used'][mountpoint] = "%.2f" % tmp
                    returnData['disk_percent'][mountpoint] = one.percent
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def get_net_info(self):
        returnData = {}
        try:
            net = psutil.net_io_counters(pernic=True)
            iplist = {}
            for name in self.ip:
                iplist[name.decode('cp936').encode('UTF8')] = self.ip[name]
            for (name, counters) in net.items():
                if 'net_packets_recv' not in returnData:
                    returnData['net_packets_recv'] = {}
                    returnData['net_packets_sent'] = {}
                    returnData['net_recv_kb'] = {}
                    returnData['net_sent_kb'] = {}
                    returnData['net_sent_rate_kbs'] = {}
                    returnData['net_recv_rate_kbs'] = {}
                name = name.decode('cp936').encode('UTF8')
                if name not in iplist:
                    continue

                returnData['net_sent_kb'][
                    name+';'+iplist[name]] = self.data_format_KB(counters.bytes_sent)
                returnData['net_recv_kb'][
                    name+';'+iplist[name]] = self.data_format_KB(counters.bytes_recv)

                returnData['net_packets_recv'][
                    name+';'+iplist[name]] = counters.packets_recv
                returnData['net_packets_sent'][
                    name+';'+iplist[name]] = counters.packets_sent
                if name not in self.oldNetSentValue:
                    self.oldNetSentValue[name] = returnData[
                        'net_sent_kb'][name+';'+iplist[name]]
                    self.oldNetRecvValue[name] = returnData[
                        'net_recv_kb'][name+';'+iplist[name]]
                tmp2 = ((returnData['net_sent_kb'][
                        name+';'+iplist[name]] - self.oldNetSentValue[name]) * 1.0 / self.interval) * 8
                returnData['net_sent_rate_kbs'][
                    name+';'+iplist[name]] = float("%.2f" % tmp2)
                tmp2 = ((returnData['net_recv_kb'][
                        name+';'+iplist[name]] - self.oldNetRecvValue[name]) * 1.0 / self.interval) * 8
                returnData['net_recv_rate_kbs'][
                    name+';'+iplist[name]] = float("%.2f" % tmp2)
                self.oldNetSentValue[name] = returnData[
                    'net_sent_kb'][name+';'+iplist[name]]
                self.oldNetRecvValue[name] = returnData[
                    'net_recv_kb'][name+';'+iplist[name]]
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def get_process_info(self):
        returnData = {}
        try:
            p = psutil.pids()
            returnData['process'] = len(p)
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def get_tcp_info(self):
        returnData = {}
        try:
            conns = psutil.net_connections()
            sumConn = {}
            for con in conns:
                if con.status == 'NONE':
                    continue
                if con.status not in sumConn:
                    sumConn[con.status] = 0
                sumConn[con.status] = sumConn[con.status] + 1
            for element in sumConn:
                if 'tcpsum' not in returnData:
                    returnData['tcpsum'] = {}
                returnData['tcpsum'][element] = sumConn[element]
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def get_linux_loadavg_info(self):
        returnData = {}
        try:
            f = open('/proc/loadavg', 'r')
            tmp = f.readline().split()
            f.close()
            returnData['lavg'] = {}
            returnData['lavg']['1min'] = float(tmp[0])
            returnData['lavg']['5min'] = float(tmp[1])
            returnData['lavg']['15min'] = float(tmp[2])
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        return returnData

    def getData(self):
        status_content = {}
        #alarm = []
        try:
            if 'cpu' in self.taskConf['type']:
                status_content['cpu'] = self.get_cpu_info()
            if 'mem' in self.taskConf['type']:
                status_content['mem'] = self.get_mem_info()
            if 'diskio' in self.taskConf['type']:
                status_content['diskio'] = self.get_disk_io_info()
            if 'diskstore' in self.taskConf['type']:
                status_content['diskstore'] = self.get_disk_rate_info()
            if 'netio' in self.taskConf['type']:
                status_content['netio'] = self.get_net_info()
            if 'procsum' in self.taskConf['type']:
                status_content['procsum'] = self.get_process_info()
            if 'tcpstatus' in self.taskConf['type']:
                status_content['tcpstatus'] = self.get_tcp_info()
            if 'loadavg' in self.taskConf['type']:
                status_content['loadavg'] = self.get_linux_loadavg_info()
            '''
            def _check():
                self.alarm = []
                reslist = ['cpu', 'mem', 'diskstore', 'diskio', 'procsum',
                           'loadavg', 'tcpstatus', 'netio']
            # 检查告警
                tmpConf = self.taskConf['snmp_list']
                for res in reslist:
                    if res in tmpConf.keys():
                        for i in tmpConf[res].items():
                            if len(i[1]) > 1:
                                tmpValue = i[1]['threshold'] * 1.00
                                alarmid = i[0]
                                action = self.option[i[1]['cond']]
                                metric = i[1]['metric']
                                result = status_content[res][metric]
                                if type(result) is not dict:
                                    checkedvalue = result
                                    if checkedvalue == action(checkedvalue, tmpValue):
                                        self.alarm.append(alarmid)
                                elif type(result) is dict:
                                    checkedvaluelist = status_content[
                                        res][metric].values()
                                    for checkedvalue in checkedvaluelist:
                                        if alarmid not in self.alarm:
                                            checkedvalue = float(checkedvalue)
                                            if checkedvalue == action(checkedvalue, tmpValue):
                                                self.alarm.append(alarmid)
            _check()
            alarm = list(set(self.alarm))
            '''
        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': status_content, 'error_info': self.error_info})
            self.intStatus()
