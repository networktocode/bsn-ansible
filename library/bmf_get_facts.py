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
module: bmf_get_facts
short_description: Get facts of a Big Switch Big Monitoring Fabric
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
- bmf_get_facts: controller=10.1.1.100 username=admin password=bsn123

'''

RETURN = '''
bsnbmf:
    description: Dictionary of facts
    returned: always
    type: dictionary
    sample:
        "bsnbcf": {
            "fabric_nodes": [
                {
                    "alias": "Filter-Switch",
                    "sw": "Switch Light Virtual 3.1.0 2015-10-07.00:17-60a8572 trusty-amd64",
                    "serial_number": "",
                    "dpid": "00:00:00:00:00:00:00:0b"
                },
                {
                    "alias": "Core-Switch",
                    "sw": "Switch Light Virtual 3.1.0 2015-10-07.00:17-60a8572 trusty-amd64",
                    "serial_number": "",
                    "dpid": "00:00:00:00:00:00:00:0c"
                },
                {
                    "alias": "Delivery-Switch",
                    "sw": "Switch Light Virtual 3.1.0 2015-10-07.00:17-60a8572 trusty-amd64",
                    "serial_number": "",
                    "dpid": "00:00:00:00:00:00:00:0d"
                }
            ],
            "vendor": "big_switch_networks",
            "platform": "N/A",
            "hostname": "N/A",
            "summary": {
                "delivery_interfaces": 2,
                "filter_interfaces": 1,
                "num_services": 0,
                "delivery_switches": 1,
                "active_policies": 0,
                "match_mode": "bigtap-l3l4",
                "total_switches": 3,
                "service_interfaces": 2,
                "num_policies": 0,
                "filter_switches": 1,
                "service_switches": 1,
                "core_interfaces": 4
            },
            "cluster": "N/A",
            "version": "N/A"
        }

'''

import json
import requests

requests.packages.urllib3.disable_warnings()


class BigCloudFabric(object):

    def __init__(self,
                 username='admin',
                 password='bsn123',
                 controller_ip='192.168.200.102',
                 port='8082',
                 protocol='http'):

        self.username = username
        self.password = password
        self.controller_ip = controller_ip
        self.port = port
        self.protocol = protocol
        self.base_url = self.protocol + '://' + self.controller_ip + ':' + self.port
        self.session_cookie = self.get_session_cookie()

    def get_session_cookie(self):
        url = self.base_url + '/auth/login'
        data = {"password": self.password, "user": self.username}
        rsp = requests.post(url, json.dumps(data), verify=False)
        return rsp.cookies

    def _make_request(self):
        # params = dict(cookies=self.session_cookie, verify=False)
        params = dict(verify=False)
        cookies = dict(session_cookie=self.session_cookie['session_cookie'])
        params['cookies'] = cookies
        if self.verb == 'GET':
            rsp = requests.get(self.url, self.data, **params)
        elif self.verb == 'PUT':
            rsp = requests.put(self.url, self.data, **params)
        elif self.verb == 'POST':
            rsp = requests.post(self.url, self.data, **params)
        return rsp

    def _execute(self):
        if not self.session_cookie:
            self.session_cookie = self.get_session_cookie()
        response = self._make_request()

        return response

    def api_call(self, uri, verb='GET', data={}):

        self.url = self.protocol + '://' + self.controller_ip + ':' + self.port + uri
        self.data = json.dumps(data)
        self.verb = verb
        output = self._execute()
        # print output.text
        json_out = json.loads(output.text)
        return json_out

    def _verb_check(self, resource_list):
        if len(resource_list) == 0:
            return 'PUT'
        else:
            return 'POST'

    def facts(self):

        # GET VERSION
        """
        uri = '/rest/v1/system/version'
        version = self.api_call(uri, 'GET')
        print version
        """

        uri = '/rest/v1/system/version' # DOESN'T WORK

        uri = '/api/v1/data/controller/core/switch'
        node_info = self.api_call(uri, 'GET')
        nodes = []
        for each in node_info:
            temp = {}
            temp['alias'] = each.get('alias')
            temp['dpid'] = each.get('dpid')
            temp['serial_number'] = each.get('attributes').get('description-data').get('serial-number')
            temp['sw'] = each.get('attributes').get('description-data').get('software-description')
            nodes.append(temp)

        uri = '/api/v1/data/controller/applications/bigtap/info'
        fabric_summary = self.api_call(uri, 'GET')[0]

        summary = dict(
            total_switches=fabric_summary.get('num-total-switches'),
            match_mode=fabric_summary.get('match-mode'),
            num_services=fabric_summary.get('num-services'),
            num_policies=fabric_summary.get('num-policies'),
            delivery_switches=fabric_summary.get("num-delivery-switches"),
            service_switches=fabric_summary.get("num-service-switches"),
            filter_switches=fabric_summary.get("num-filter-switches"),
            active_policies=fabric_summary.get("num-active-policies" ),
            core_interfaces=fabric_summary.get("num-core-interfaces" ),
            delivery_interfaces=fabric_summary.get("num-delivery-interfaces" ),
            service_interfaces=fabric_summary.get("num-service-interfaces" ),
            filter_interfaces=fabric_summary.get("num-filter-interfaces" ),
            )


        facts = {}
        facts['cluster'] = 'N/A'
        facts['fabric_nodes'] = nodes
        facts['vendor'] = 'big_switch_networks'
        facts['summary'] = summary
        facts['version'] = 'N/A'
        facts['platform'] = 'N/A'
        facts['hostname'] = 'N/A'

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

    module.exit_json(ansible_facts=dict(bsnbmf=facts))


def test():
    controller = '54.161.99.67'
    username = 'admin'
    password = 'bsn123'

    fabric = BigCloudFabric(controller_ip=controller,
                            username=username,
                            password=password)

    facts = fabric.facts()

    print json.dumps(facts, indent=4)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
