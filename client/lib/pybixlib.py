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

import os
import time
import datetime
import logging
import sys
import socket


def date(unixtime, format='%m/%d/%Y %H:%M'):
    d = datetime.datetime.fromtimestamp(unixtime)
    return d.strftime(format)


def strtotime(timeStr, format='%Y-%m-%d %H:%M:%S'):
    time_tuple = time.strptime(timeStr, format)
    timestamp = time.mktime(time_tuple)
    return int(timestamp)


def info(log_msg):
    logger = logging.getLogger('pybix')
    FileHandler = logging.FileHandler(
        getPath() + "/log/" + date(time.time(), format='%Y-%m-%d')+'.log')
    FileHandler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(FileHandler)
    logger.setLevel(logging.INFO)
    logger.info(log_msg)
    logger.removeHandler(FileHandler)
    FileHandler.close()


def error(log_msg):
    logger = logging.getLogger('pybix')
    FileHandler = logging.FileHandler(
        getPath() + "/log/" + date(time.time(), format='%Y-%m-%d')+'.log')
    FileHandler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(FileHandler)
    logger.setLevel(logging.INFO)
    logger.error(log_msg)
    logger.removeHandler(FileHandler)
    FileHandler.close()


def getPath():
    str = os.path.split(os.path.realpath(__file__))
    str = os.path.split(str[0])
    return str[0]+'/'


def printout(data):
    sys.stderr.write(data+'\n')


def get_mac_address():
    import uuid
    node = uuid.getnode()
    mac = uuid.UUID(int=node).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0, 11, 2)])


def get_hostname():
    return socket.gethostname()


def get_ipList():
    ipList = socket.gethostbyname_ex(get_hostname())[2]
    try:
        ipList.remove("127.0.0.1")
    except:
        None
    finally:
        return ",".join(ipList)
