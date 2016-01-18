#!/usr/bin/env python

# Copyright 2016 Jason Edelman <jason@networktocode.com>
# Network to Code, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = '''
---
module: bcf_get_facts
short_description: Get facts of a Big Switch Big Cloud Fabric
description:
    - Get facts of a Big Switch Big Cloud Fabric
author: Jason Edelman (@jedelman8)
version_added: 1.9.2
options:
    controller:
        description:
            - Hostame or IP address of BCF controller.
        required: true
    username:
        description:
            - Username used to login to the controller
        required: true
    password:
        description:
            - Password used to login to the controller
        required: true
'''

EXAMPLES = '''
- bcf_get_facts: controller=10.1.1.100 username=admin password=bsn123

'''

RETURN = '''
bsnbcf:
    description: Dictionary of facts
    returned: always
    type: dictionary
    sample:
        "bsnbcf": {
            "cluster": {
                "controllers": [
                    {
                        "hostname": "10.10.12.20",
                        "role": "active",
                        "uptime": 33807223
                    }
                ],
                "description": null,
                "name": "bigswitchcluster",
                "redundancy_status": {
                    "msg": "Single node configured",
                    "status": "standalone"
                },
                "virtual_ip": null
            },
            "fabric_nodes": [
                {
                    "dpid": "00:00:00:00:00:02:00:01",
                    "fabric_state": "connected",
                    "name": "R1L1",
                    "role": "leaf",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:02:00:02",
                    "fabric_state": "connected",
                    "name": "R1L2",
                    "role": "leaf",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:02:00:03",
                    "fabric_state": "connected",
                    "name": "R2L1",
                    "role": "leaf",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:02:00:04",
                    "fabric_state": "connected",
                    "name": "R2L2",
                    "role": "leaf",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:02:00:05",
                    "fabric_state": "connected",
                    "name": "R3L1",
                    "role": "leaf",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:02:00:06",
                    "fabric_state": "connected",
                    "name": "R3L2",
                    "role": "leaf",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:01:00:01",
                    "fabric_state": "connected",
                    "name": "S1",
                    "role": "spine",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:01:00:02",
                    "fabric_state": "connected",
                    "name": "S2",
                    "role": "spine",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                },
                {
                    "dpid": "00:00:00:00:00:01:00:03",
                    "fabric_state": "connected",
                    "name": "S3",
                    "role": "spine",
                    "sw": "Switch Light Virtual 3.5.0 2015-12-15.00:38-db7144c trusty-amd64"
                }
            ],
            "hostname": "controller",
            "platform": "Big Cloud Fabric Appliance 3.5.0 (bcf-3.5.0 #75)",
            "summary": {
                "controllers": 1,
                "errors": 18,
                "leaf_groups_configured": 3,
                "leaves_configured": 6,
                "leaves_connected": 6,
                "overall_status": "NOT OK",
                "spines_configured": 3,
                "spines_connected": 3,
                "tenants": 0,
                "vswitches_connected": 0,
                "warnings": 14
            },
            "vendor": "big_switch_networks",
            "version": "3.5.0"
        }
    }
}


'''

import json
import requests

requests.packages.urllib3.disable_warnings()


class BigCloudFabric(object):

    def __init__(self,
                 username='admin',
                 password='bsn123',
                 controller_ip='192.168.200.102'):

        self.username = username
        self.password = password
        self.controller_ip = controller_ip
        self.base_url = 'https://' + self.controller_ip + ':8443'
        self.session_cookie = self.get_session_cookie()

    def get_session_cookie(self):
        url = self.base_url + '/api/v1/auth/login'
        data = {"password": self.password, "user": self.username}
        rsp = requests.post(url, json.dumps(data), verify=False)

        return rsp.cookies

    def _make_request(self):
        params = dict(cookies=self.session_cookie, verify=False)
        if self.verb == 'GET':
            rsp = requests.get(self.url, **params)
        elif self.verb == 'PUT':
            rsp = requests.put(self.url, self.data, **params)
        elif self.verb == 'POST':
            rsp = requests.post(self.url, self.data, **params)
        return rsp

    def _execute(self):
        if not self.session_cookie:
            self.get_session_cookie()
        response = self._make_request()

        return response

    def api_call(self, uri, verb='GET', data={}):
        self.url = self.base_url + uri
        self.data = json.dumps(data)
        self.verb = verb
        output = self._execute()
        json_out = json.loads(output.text)
        return json_out

    def _verb_check(self, resource_list):
        if len(resource_list) == 0:
            return 'PUT'
        else:
            return 'POST'

    def facts(self):

        # GET VERSION
        uri = '/api/v1/data/controller/core/version/appliance'
        version = self.api_call(uri, 'GET')[0]

        # GET HOSTNAME
        uri = '/api/v1/data/controller/os/config/local?config=true'
        data = self.api_call(uri, 'GET')[0]
        local_hostname = data['network']['hostname']

        # GET CLUSTER INFORMATION
        uri = '/api/v1/data/controller/cluster'
        cluster_data = self.api_call(uri, 'GET')[0]

        cluster_name = cluster_data['name']
        description = None
        if cluster_data.get('description'):
            description = cluster_data['description']

        uri = '/api/v1/data/controller/core/high-availability/redundancy-status'
        ha = self.api_call(uri, 'GET')[0]

        rstatus = {'status': ha['status'], 'msg': ha['message']}

        uri = '/api/v1/data/controller/core/high-availability/node'
        controllers_info = self.api_call(uri, 'GET')

        controllers = []
        for each in controllers_info:
            temp = {}
            temp['hostname'] = each.get('hostname')
            temp['uptime'] = each.get('uptime')
            temp['role'] = each.get('role')
            controllers.append(temp)

        # GET INFO ON ALL NODES IN FABRIC
        uri = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
        node_info = self.api_call(uri, 'GET')

        nodes = []
        for each in node_info:
            temp = {}
            temp['name'] = each.get('name')
            temp['role'] = each.get('fabric-role')
            temp['dpid'] = each.get('dpid')
            temp['fabric_state'] = each.get('fabric-connection-state')
            temp['sw'] = each.get('software-description')
            nodes.append(temp)

        # GET VIP OF CONTROLLER
        uri = '/api/v1/data/controller/os/config/global/virtual-ip'
        vip_info = self.api_call(uri, 'GET')[0]
        vip = None
        if vip_info.get('ipv4-address'):
            vip = vip_info['ipv4-address']

        cluster = dict(
                name=cluster_name,
                description=description,
                redundancy_status=rstatus,
                controllers=controllers,
                virtual_ip=vip
                )

        uri = '/api/v1/data/controller/applications/bcf/info/summary/fabric'
        fabric_summary = self.api_call(uri, 'GET')[0]

        summary = dict(
            overall_status=fabric_summary.get('overall-status'),
            errors=fabric_summary.get('errors'),
            warnings=fabric_summary.get('warnings'),
            leaves_configured=fabric_summary.get("num-leaves-configured"),
            leaf_groups_configured=fabric_summary.get("num-leaf-groups-configured"),
            controllers=fabric_summary.get("num-controller-nodes" ),
            spines_configured=fabric_summary.get("num-spines-configured" ),
            spines_connected=fabric_summary.get("num-spines-connected"),
            tenants=fabric_summary.get("tenant-count"),
            leaves_connected=fabric_summary.get("num-leaves-connected" ),
            vswitches_connected=fabric_summary.get("num-vswitches-connected")
            )

        facts = {}
        facts['cluster'] = cluster
        facts['fabric_nodes'] = nodes
        facts['version'] = version['version']
        facts['platform'] = version['release-string']
        facts['hostname'] = local_hostname
        facts['vendor'] = 'big_switch_networks'
        facts['summary'] = summary

        return facts


def main():
    module = AnsibleModule(
        argument_spec=dict(
            controller=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
        ),
        supports_check_mode=False
    )

    controller = module.params['controller']
    username = module.params['username']
    password = module.params['password']

    fabric = BigCloudFabric(controller_ip=controller,
                            username=username,
                            password=password)

    facts = fabric.facts()

    module.exit_json(ansible_facts=dict(bsnbcf=facts))

"""
def test():
    controller = '52.91.137.171'
    username = 'admin'
    password = 'bsn123'

    fabric = BigCloudFabric(controller_ip=controller,
                            username=username,
                            password=password)

    facts = fabric.facts()

    print json.dumps(facts, indent=4)
"""

from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
