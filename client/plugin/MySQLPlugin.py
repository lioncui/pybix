#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib import pybixlib
import traceback
from p_class import plugins
import pymysql


class MySQLPlugin(plugins.plugin):

    def __init__(self, uuid, taskConf, agentType):
        plugins.plugin.__init__(
            self, uuid, taskConf, agentType)

    def getData(self):
        redata = {}
        try:
            host = self.taskConf.get("host")
            port = self.taskConf.get("port")
            user = self.taskConf.get("user")
            password = self.taskConf.get("password")

            key_variables = ['log_slow_queries', 'slow_launch_time', 'max_connections', 'key_buffer_size',
                             'tmp_table_size', 'max_heap_table_size', 'table_open_cache', 'thread_cache_size', 'query_cache_limit',
                             'query_cache_min_res_unit', 'query_cache_size', 'query_cache_type', 'query_cache_wlock_invalidate',
                             'open_files_limit']

            key_status = ['Slow_launch_threads', 'Slow_queries', 'Max_used_connections', 'Key_read_requests',
                          'Key_reads', 'Key_blocks_unused', 'Key_blocks_used', 'Created_tmp_disk_tables', 'Created_tmp_files',
                          'Created_tmp_tables', 'Open_tables', 'Opened_tables', 'Threads_cached', 'Threads_connected',
                          'Threads_created', 'Threads_running', 'Qcache_free_blocks', 'Qcache_free_memory', 'Qcache_hits',
                          'Qcache_inserts', 'Qcache_lowmem_prunes', 'Qcache_not_cached', 'Qcache_queries_in_cache',
                          'Qcache_total_blocks', 'Sort_merge_passes', 'Sort_range', 'Sort_rows', 'Sort_scan', 'Open_files',
                          'Table_locks_immediate', 'Table_locks_waited', 'Handler_read_first', 'Handler_read_key',
                          'Handler_read_next', 'Handler_read_prev', 'Handler_read_rnd', 'Handler_read_rnd_next', 'Com_change_db',
                          'Com_delete', 'Com_insert', 'Com_select', 'Com_update', 'Com_update_multi', 'Connections',
                          'Bytes_received', 'Bytes_sent', 'Innodb_buffer_pool_read_requests', 'Innodb_buffer_pool_reads', 'Com_commit', 'Com_rollback', 'Queries', 'Uptime']

            key_other = ['QCACHE_USE_RATE']

            keys = ''
            for key in key_variables:
                keys += "'" + key + "',"
            keys = keys.strip(',')

            conn = pymysql.connect(host=host, port=port,
                                   user=user, password=password,
                                   charset="utf8", cursorclass=pymysql.cursors.DictCursor
                                   )
            try:
                with conn.cursor() as cur:
                    sql = "show variables where Variable_name in (" + \
                        keys + ")"
                    cur.execute(sql)
                    results = cur.fetchall()
                    for result in results:
                        key = result['Variable_name']
                        value = result['Value']
                        redata[key] = value

                    keys = ''
                    for key in key_status:
                        keys += "'"+key+"',"
                    keys = keys.strip(',')
                    sql = "show global status where Variable_name in (" + \
                        keys + ")"
                    cur.execute(sql)
                    results = cur.fetchall()
                    for result in results:
                        key = result['Variable_name']
                        value = result['Value']
                        redata[key] = value

                    for key in key_other:
                        if key == 'QCACHE_USE_RATE':
                            if redata['query_cache_size'] == float(0):
                                redata['QCACHE_USE_RATE'] = "0"
                            else:
                                t = float(redata['query_cache_size'])
                                f = float(redata['Qcache_free_memory'])
                                redata['QCACHE_USE_RATE'] = float(
                                    (t - f) / f) * 100.00

            finally:
                conn.close()

        except Exception:
            pybixlib.error(self.logHead + traceback.format_exc())
            self.errorInfoDone(traceback.format_exc())
            redata = {}
        finally:
            self.setData({'agentType': self.agentType, 'uuid': self.uuid,
                          'code': self.code, 'time': self.getCurTime(),
                          'data': redata, 'error_info': self.error_info})
            self.intStatus()
