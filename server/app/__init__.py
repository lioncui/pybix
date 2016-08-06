#/usr/bin/python
# -*- coding:utf8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_mongoengine import MongoEngine
import logging
import os


app = Flask(__name__)
app.config.from_object('config')
api = Api(app)
db = SQLAlchemy(app)
mongo = MongoEngine(app)

from app import views, models


logpath = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0]
handler = logging.FileHandler(
    logpath + '/log/pybix-server.log', encoding='UTF-8')
handler.setLevel(logging.DEBUG)
logging_format = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(logging_format)
app.logger.addHandler(handler)
