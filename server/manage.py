#!/usr/bin/python
# -*- coding:utf8 -*-

from flask_script import Manager, Server
from app import app, db

manager = Manager(app)

manager.add_command(
    "runserver", Server(host="0.0.0.0", port=8080, use_debugger=False))


@manager.command
def sync():
    '''sync database to create tables. '''
    db.create_all()


if __name__ == '__main__':
    manager.run()
