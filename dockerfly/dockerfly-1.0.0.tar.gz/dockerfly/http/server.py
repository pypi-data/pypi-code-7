#!/bin/env python
# -*- coding: utf-8 -*-

import json
import time
from flask import Flask, request
from flask import json
from flask.ext.restful import reqparse, abort, Api, Resource

from dockerfly.settings import dockerfly_version
from dockerfly.runtime import container as ContainerStatus
from dockerfly.dockerlib.container import Container as ContainerCtl

dockerfly_app = Flask(__name__)
dockerfly_api = Api(dockerfly_app)

def abort_if_container_doesnt_exist(container_id):
    for item in ContainerStatus.get_all_status():
        if len(container_id) >= 12 and item['id'].startswith(container_id):
            return item['id']
    abort(404, message="Container {} doesn't exist".format(container_id))

class Version(Resource):
    def get(self):
        return {'version':dockerfly_version}

class ContainerList(Resource):
    def get(self):
        return ContainerStatus.get_all_status()

    def post(self):
        """json template

            {
                "eths": [
                    [
                        "testDockerflyv0",
                        "eth0",
                        "172.16.11.239/24"
                    ]
                ],
                "gateway": "172.16.11.1",
                "id": null,
                "pid": null,
                "image_name": "centos:centos6_sshd",
                "container_name": "testDockerflyxxx",
                "last_modify_time": 0,
                "run_cmd": "/usr/sbin/sshd -D",
                "status": "running",
                "desc": "create a container by template"
            }
        """
        create_containers_json = request.get_json()
        for container in create_containers_json:
            container['id'] = ContainerCtl.create(container['image_name'],
                                                  container['run_cmd'],
                                                  container['container_name'])
            ContainerCtl.start(container['id'],
                               container['eths'],
                               container['gateway'])
            if container.get('resize', None):
                ContainerCtl.resize(container['id'], container['resize'])
            container['pid'] = ContainerCtl.get_pid(container['id'])
            container['last_modify_time'] = time.time()
        ContainerStatus.add_status(create_containers_json)
        return create_containers_json, 201

class Container(Resource):
    def get(self, container_id):
        container_id = abort_if_container_doesnt_exist(container_id)
        return ContainerStatus.get_status(container_id), 200

    def delete(self, container_id):
        container_id = abort_if_container_doesnt_exist(container_id)
        ContainerCtl.remove(container_id)
        ContainerStatus.remove_status([container_id])
        return {'msg':'OK'}, 200

class ContainerActive(Resource):
    def put(self, container_id):
        container_id = abort_if_container_doesnt_exist(container_id)
        container_status = ContainerStatus.get_status(container_id)
        if container_status['status'] == 'stopped':
            ContainerCtl.start(container_id, container_status['eths'],
                                             container_status['gateway'])
            container_status['last_modify_time'] = time.time()
            container_status['status'] = 'running'
            ContainerStatus.update_status([container_status])
            return container_status, 202
        else:
            return {'errMsg': 'container is running'}, 400

class ContainerInactive(Resource):
    def put(self, container_id):
        container_id = abort_if_container_doesnt_exist(container_id)
        container_status = ContainerStatus.get_status(container_id)
        if container_status['status'] == 'running':
            ContainerCtl.stop(container_id)
            container_status['last_modify_time'] = time.time()
            container_status['status'] = 'stopped'
            ContainerStatus.update_status([container_status])
            return container_status, 202
        else:
            return {'errMsg': 'container is stopped'}, 400

class ContainerTaskList(Resource):
    def post(self, container_id):
        container_id = abort_if_container_doesnt_exist(container_id)
        return {'errMsg':'Not Implement'}, 400

class ContainerTask(Resource):
    def get(self, task_id):
        return {'errMsg':'Not Implement'}, 400

    def delete(self, task_id):
        return {'errMsg':'Not Implement'}, 400

dockerfly_api.add_resource(Version, '/v1/version')
dockerfly_api.add_resource(ContainerList, '/v1/containers')
dockerfly_api.add_resource(Container, '/v1/container/<string:container_id>')
dockerfly_api.add_resource(ContainerActive, '/v1/container/<string:container_id>/active')
dockerfly_api.add_resource(ContainerInactive, '/v1/container/<string:container_id>/inactive')
dockerfly_api.add_resource(ContainerTaskList, '/v1/container/<string:container_id>/tasks')
dockerfly_api.add_resource(ContainerTask, '/v1/container/<string:container_id>/task/<string:task_id>')

def run_server(debug=False):
    dockerfly_app.run(use_debugger=debug, debug=debug, use_reloader=False, host='0.0.0.0', port=5123)

if __name__ == '__main__':
    run_server(True)
