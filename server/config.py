#!/usr/bin/python
# -*- coding:utf8 -*-

DBUSER = 'root'
DBPASS = '123456'
DBHOST = '127.0.0.1'
DBPORT = '3306'
DBNAME = 'pybix'
DEBUG = False
PORT = 8080
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://%s:%s@%s:%s/%s" % (
    DBUSER, DBPASS, DBHOST, DBPORT, DBNAME)
SQLALCHEMY_TRACK_MODIFICATIONS = False

MONGODB_SETTINGS = {'HOST': 'localhost', 'PORT': 27017, 'DB': 'pybix'}
SECRET_KEY = "4RTG2WQSUHEDUJ"
PRE_SHARE_KEY = "7Y5TGH76RFGH6RFGHY5RDCVHY2W34"
