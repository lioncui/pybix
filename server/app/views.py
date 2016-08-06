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
# -*- coding:utf8 -*-

from app import app
from app import api
from app import db
from app import models
from flask_restful import Resource
from flask import jsonify
from flask import request
from datetime import datetime
from uuid import uuid4


def create_uuid():
    id_team = str(uuid4()).split("-")
    sort_id = "".join(id_team)
    return sort_id[:16]


def orm_obj_to_dict(obj):
    obj_dict = {}
    try:
        tablename = obj.__tablename__
        columns = db.session.execute(
            "select COLUMN_NAME from information_schema.COLUMNS where table_name = '%s'" % tablename).fetchall()
        for key in columns:
            obj_dict[key[0]] = getattr(obj, key[0])
            if isinstance(obj_dict[key[0]], datetime):
                obj_dict[key[0]] = obj_dict[
                    key[0]].strftime('%Y-%m-%d %H:%M:%S')
        app.logger.info("Executive function orm_obj_to_dict.")
    except Exception:
        obj_dict = {}
        app.logger.error("The orm objects into json faild.")
    finally:
        return obj_dict


class HostsController(Resource):

    def get(self):
        hostlist = []
        for host in models.Hosts.query.all():
            hostlist.append(orm_obj_to_dict(host))
        app.logger.info("GET /hosts - OK.")
        return jsonify(hosts=hostlist)

    def post(self):
        try:
            args = request.json
            host = models.Hosts(timestamp=datetime.now(), **args)
            db.session.add(host)
            db.session.commit()
            app.logger.info("POST /hosts - OK.")
            return orm_obj_to_dict(host)
        except Exception, e:
            db.session.rollback()
            app.logger.error("POST /hosts - Create host faild.")
            return jsonify(status="error", message=str(e)), 500
        finally:
            db.session.close()

    def delete(self):
        try:
            args = request.json
            host = models.Hosts.query.filter_by(mac=args.get("mac")).first()
            if host is not None:
                db.session.delete(host)
                db.session.commit()
                app.logger.info("%s /hosts - OK." % "delete".upper())
                return jsonify(status="ok")
            else:
                raise ValueError("can not found host")
        except Exception, e:
            db.session.rollback()
            app.logger.error(
                "%s /hosts - delete host faild." % "delete".upper())
            return jsonify(status="error", message=str(e)), 500
        finally:
            db.session.close()


class HostController(Resource):

    def get(self, mac):
        try:
            host = models.Hosts.query.filter_by(mac=mac).first()
            redata = orm_obj_to_dict(host)
            if redata == {}:
                app.logger.warning("GET /hosts/<mac> - resource not found.")
                return {"status": "error", "message": "resource not found"}, 400
            else:
                app.logger.info("GET /hosts/<mac> - OK.")
                return redata
        except Exception, e:
            app.logger.error("GET /hosts/<mac> - faild")
            return jsonify(status="error", message=str(e)), 500


class TasksController(Resource):

    def get(self):
        try:
            tasklist = {}
            for task in models.Tasks.query.all():
                new_task_obj = orm_obj_to_dict(task)
                new_task_obj['taskConf'] = eval(new_task_obj['taskConf'])
                single_task = {new_task_obj['uuid']: new_task_obj}
                tasklist.update(single_task)
            app.logger.info("GET /tasks - OK.")
            return jsonify(tasks=tasklist)
        except IndexError:
            app.logger.warning("GET /tasks - resource not found")
            return jsonify(status="error", message="resource not found"), 400

    def post(self):
        try:
            get_args = request.json
            args = {x: str(get_args[x]) for x in get_args}
            task = models.Tasks(
                uuid=create_uuid(), timestamp=datetime.now(), **args)
            db.session.add(task)
            db.session.commit()
            app.logger.info("POST /tasks - OK.")
            return orm_obj_to_dict(task)
        except Exception, e:
            db.session.rollback()
            app.logger.error("POST /tasks - Create task faild.")
            return jsonify(status="error", message=str(e)), 500
        finally:
            db.session.close()


class TaskController(Resource):

    def get(self, mac):
        try:
            tasklist = {}
            for task in models.Tasks.query.filter_by(host_mac=mac).all():
                new_task_obj = orm_obj_to_dict(task)
                new_task_obj['taskConf'] = eval(new_task_obj['taskConf'])
                single_task = {new_task_obj['uuid']: new_task_obj}
                tasklist.update(single_task)
            app.logger.info("GET /tasks/<mac> - OK.")
            return jsonify(tasks=tasklist)
        except Exception, e:
            app.logger.warning("GET /task/<mac> - resource not found.")
            return jsonify(status="error", message=str(e)), 400

    def put(self):
        pass

    def delete(self):
        pass


class MetersController(Resource):

    def get(self, uuid):
        meters = models.Resources.objects.filter(
            task_uuid=uuid).order_by("-timestamp").first()
        app.logger.info("GET /meters/<task_uuid> - OK.")
        return eval(meters.data)

    def post(self, uuid):
        try:
            data = request.json
            res = models.Resources(
                task_uuid=uuid, data=str(data), timestamp=datetime.now())
            res.save()
            app.logger.info("POST /meters/<task_uuid> - OK.")
        except Exception:
            pass


api.add_resource(HostsController, '/hosts')
api.add_resource(HostController, '/hosts/<string:mac>')
api.add_resource(TasksController, '/tasks')
api.add_resource(TaskController, '/tasks/<string:mac>')
api.add_resource(MetersController, '/meters/<string:uuid>')
