#!/usr/bin/python
# -*- coding:utf8 -*-


from app import db
from app import mongo


class Hosts(db.Model):
    __tablename__ = 'HOSTS'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    mac = db.Column(db.String(18), unique=True)
    hostname = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime)
    tasks = db.relationship('Tasks', backref="HOSTS", lazy="dynamic")

    def __repr__(self):
        return '<Host %r>' % (self.mac)


class Tasks(db.Model):
    __tablename__ = 'TASKS'
    uuid = db.Column(db.String(32), primary_key=True, unique=True)
    agentType = db.Column(db.String(20))
    pluginClassName = db.Column(db.String(80))
    pluginFileName = db.Column(db.String(80))
    status = db.Column(db.Integer, default=1)
    taskConf = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime)
    host_mac = db.Column(db.String(18), db.ForeignKey('HOSTS.mac'))

    def __repr__(self):
        return '<Task %r>' % (self.uuid)


class Resources(mongo.Document):
    task_uuid = mongo.StringField(required=True)
    data = mongo.StringField(required=True)
    timestamp = mongo.DateTimeField()
