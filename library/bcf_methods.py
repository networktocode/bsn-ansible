#!/usr/bin/env python

import urllib2
import json


class BigCloudFabric(object):

    PROTOCOL = 'https'
    PORT = '8443'

    def __init__(self, username='admin', password='bigswitch',
                 controller_ip='192.168.200.102'):

        self.session_cookie = None

        self.username = username
        self.password = password
        self.controller_ip = controller_ip
        self.session_cookie = self.get_session_cookie()
        # gets session cookie on initialization
        # not sure how long this is valid for

    def rest_request(self, url, obj, verb='GET'):
        headers = {'Content-type': 'application/json'}

        # if we have session variables add them
        if self.session_cookie:
            headers["Cookie"] = "session_cookie=%s" % self.session_cookie
            request = urllib2.Request(url, obj, headers)
            request.get_method = lambda: verb
            response = urllib2.urlopen(request)
            result = response.read()
            return result
        else:
            request = urllib2.Request(url, obj, headers)
            request.get_method = lambda: verb
            response = urllib2.urlopen(request)
            result = response.read()
            return result

    def get_session_cookie(self):

        urlLogin = 'https://' + self.controller_ip + ':8443/api/v1/auth/login'
        data1 = {"password": str(self.password), "user": str(self.username)}
        output = self.rest_request(str(urlLogin), json.dumps(data1), "POST")
        authObj = json.loads(output)
        return authObj["session_cookie"]

    def get_api_call(self, uri, verb='GET', data=None):
        # empty data dictionary for GET APIs
        url = 'https://' + self.controller_ip + ':8443' + uri

        if verb == 'GET':
            data = {}

        obj = json.dumps(data)
        output = self.rest_request(url, obj, verb)
        json_out = json.loads(output)

        return json_out

    def api_call(self, uri, verb='GET', data=None):
        url = 'https://' + self.controller_ip + ':8443' + uri

        if verb == 'GET':
            data = {}

        obj = json.dumps(data)
        output = self.rest_request(url, obj, verb)

    def get_switches(self):
        uri = '/api/v1/data/controller/core/switch-config'
        switches = self.get_api_call(uri, 'GET')
        return switches

    def remove_switch(self, name):
        data = {}
        uri = '/api/v1/data/controller/core/switch-config[name="' + name + '"]'
        self.api_call(uri, 'DELETE', data)

    def provision_switch(self, name, mac_address, role, group=None):
        switches = self.get_switches()
        # print json.dumps( switches, indent=4)
        verb = self.verb_check(switches)
        exists, dummy = self.resource_exists(switches, 'name', name)

        if not exists:
            data = {'dpid': '00:00:' + mac_address,
                    'name': name, 'fabric-role': role}
            uri = '/api/v1/data/controller/core/switch-config'
            self.api_call(uri, verb, data)
        else:
            msg = 'Device already loaded in controller'

    def get_tenants(self):
        uri = '/api/v1/data/controller/applications/bcf/tenant'
        tenants = self.get_api_call(uri, 'GET')
        return tenants

    def create_tenant(self, tenant_name):
        tenants = self.get_tenants()
        # print json.dumps( tenants, indent=4)
        verb = self.verb_check(tenants)
        exists, dummy = self.resource_exists(tenants, 'name', tenant_name)
        if not exists:
            data = {'name': tenant_name}
            uri = '/api/v1/data/controller/applications/bcf/tenant'
            self.api_call(uri, verb, data)
            return True
        else:
            return False  # 'Tenant already created in controller'

    def get_switches_standalone(self):

        uri = '/api/v1/data/controller/core/zerotouch/device'
        r5 = self.get_api_call(uri, 'GET')
        devices = {}
        temp = {}
        nodes = {}
        for each in r5:
            if each.has_key('name'):
                key = each['name']
                devices[key] = each
                devices[key].pop('reload-pending')
                devices[key].pop('dpid')

                for k, v in devices[key].iteritems():
                    k1 = str(k)
                    v1 = str(v)
                    temp[k1] = str(v1)
                    key = str(key)
                nodes[key] = temp

        orig = self.get_switches()
        for each in orig:
            key = each['name']
            nodes[key].update(each)

        return nodes

    def delete_tenant(self, tenant_name):
        data = {}
        uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]'
        self.api_call(uri, 'DELETE', data)
        # print json.dumps( tenants, indent=4)

    def delete_segment(self, tenant_name, segment_name):
        data = {'name': segment_name}
        uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/segment[name="%s"]' %segment_name
        self.api_call(uri, 'DELETE', data)

    def get_segments(self, tenant_name):
        uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/segment'
        segments = self.get_api_call(uri, 'GET')
        return segments

    def resource_exists(self, resource_list, key, value):
        '''
        accept a list of dictionaries and searches
        the list of dictionaries. if a key/value pair is found
        return true, else return false
        '''
        exists = False, {}
        for each in resource_list:
            if each[key] == value:
                exists = True, each
        return exists

    def create_segment(self, tenant_name, segment_name,
                       vlan_id, port_group, interfaces, switch):
        segments = self.get_segments(tenant_name)
        verb = self.verb_check(segments)

        exists, dummy = self.resource_exists(segments, 'name', segment_name)

        if not exists:
            data = {'name': segment_name}
            uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/segment'
            self.api_call(uri, verb, data)

            uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/segment[name="%s"]/port-group-membership-rule' %segment_name
            data = {"vlan": vlan_id, "port-group": port_group }
            self.api_call(uri, verb, data)

            uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/segment[name="%s"]/switch-port-membership-rule' %segment_name
            data = {"vlan": vlan_id, "switch": switch, "interface": interfaces}
            self.api_call(uri, verb, data)
            return True
        else:
            return False  # 'Segment already configured in controller'

    def delete_logical_segment_interface(self, tenant_name, segment):

        data = {}
        uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/logical-router/segment-interface[segment= "'+ segment +'"]'
        self.api_call(uri, 'DELETE', data)

    def get_logical_interfaces(self, tenant_name):
        uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/logical-router'
        logical_interfaces = self.get_api_call(uri, 'GET')
        # returns a list of dictionaries - one dict per segment
        return logical_interfaces

    def logical_interface_exist(self, tenant_name,
                                logical_interfaces_in_tenant, segment):
        match = False, {}
        for each in logical_interfaces_in_tenant:
            for key, value in each.iteritems():
                if key == 'segment-interface':
                    for segment_interface in value:
                        if segment == segment_interface['segment']:
                            match = True, segment_interface
        return match

    def create_logical_segment_interface(self, tenant_name, segment, lr_ip):

        logical_interfaces_in_tenant = self.get_logical_interfaces(tenant_name)
        # print json.dumps( lrs, indent=4)
        verb = self.verb_check(logical_interfaces_in_tenant)
        exists, config = self.logical_interface_exist(tenant_name,
                                                      logical_interfaces_in_tenant,
                                                      segment)

        # keeping API calls separate to ease troubleshooting at this time
        if not exists:
            data = {}
            uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/logical-router'
            self.api_call(uri, verb, data)

            data = {'segment': segment}
            uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/logical-router/segment-interface'
            self.api_call(uri, verb, data)

            data = {"ip-cidr": lr_ip, "private": "false"}
            uri = '/api/v1/data/controller/applications/bcf/tenant[name="' + tenant_name + '"]/logical-router/segment-interface[segment= "'+ segment +'"]/ip-subnet'
            self.api_call(uri, verb, data)
        else:
            msg = 'Logical router interface for the segment already configured'
            # not being returned - can be used for tshooting

    def verb_check(self, resource_list):
        if len(resource_list) == 0:
            return 'PUT'
        else:
            return 'POST'

    def facts(self):
        '''
        Started to convert unicode to strings, but never finished
        '''

        uri = '/api/v1/data/controller/core/version/appliance'
        r1 = self.get_api_call(uri, 'GET')[0]

        uri = '/api/v1/data/controller/cluster'
        r2 = self.get_api_call(uri, 'GET')[0]
        cluster_name = r2['name']
        if r2.has_key('description'):
            description = r2['description']
        else:
            description = 'None set (null)'

        uri = '/api/v1/data/controller/core/high-availability/redundancy-status'
        r3 = self.get_api_call(uri, 'GET')[0]
        rstatus = {'status': str(r3['status']), 'msg': str(r3['message'])}

        uri = '/api/v1/data/controller/core/high-availability/node'
        r4 = self.get_api_call(uri, 'GET')
        controllers = {}
        temp = {}
        ctrls = {}
        for each in r4:
            key = each['hostname']
            controllers[key] = each
            controllers[key].pop('node-id')

            for k, v in controllers[key].iteritems():
                k1 = str(k)
                v1 = str(v)
                temp[k1] = str(v1)
                key = str(key)
            ctrls[key] = temp

        # uri = '/api/v1/data/controller/core/zerotouch/device'
        uri = '/api/v1/data/controller/applications/bcf/info/fabric/switch'
        r5 = self.get_api_call(uri, 'GET')
        # print json.dumps(r5, indent=4)
        # print '444444444444444'
        devices = {}
        temp = {}
        nodes = []
        for each in r5:
            key = each.get('name')
            if key:
                temp = {}
                temp['name'] = each.get('name')
                temp['role'] = each.get('fabric-role')
                temp['dpid'] = each.get('dpid')
                temp['fabric_state'] = each.get('fabric-connection-state')
                temp['sw'] = each.get('software-description')
                nodes.append(temp)

        uri = '/api/v1/data/controller/os/config/local?config=true'
        r6 = self.get_api_call(uri, 'GET')[0]
        local_hostname = r6['network']['hostname']

        path = r6['network']['interface'][0]['ipv4']['dns']
        if path.has_key('search-path'):
            if len(path['search-path']) == 1:
                domain = path['search-path'][0]
            else:
                domain = path['search-path']
        else:
            domain = 'None_set_(null)'

        uri = '/api/v1/data/controller/os/config/global/virtual-ip'
        r7 = self.get_api_call(uri, 'GET')[0]
        if r7.has_key('ipv4-address'):
            vip = r7['ipv4-address']
        else:
            vip = 'None_set_(null)'

        cluster = dict(
                name=str(cluster_name),
                description=str(description),
                redundancy_status=rstatus,
                controllers=ctrls,
                virtual_ip=str(vip)
                )
        facts = {}
        facts['bsn'] = {'cluster': cluster, 'fabric_nodes': nodes}
        facts['version'] = str(r1['version'])
        facts['hostname'] = str(local_hostname)
        facts['domainname'] = str(domain)
        facts['vendor'] = 'big_switch_networks'

        return facts


def main():

    fab = BigCloudFabric(controller_ip='52.91.237.106',
                         username='admin', password='bsn123')

    ##################
    # ## GET FACTS  ###
    ##################
    facts = fab.facts()
    print json.dumps(facts, indent=4)
    print '=' * 50
    '''
    #########################
    # ## PROVISION LEAF1  ###
    #########################
    name = 'leaf-1'
    mac_address = '70:72:cf:bd:de:78'
    role = 'leaf'
    group = 'leafs-rack1'

    fab.provision_switch(name, mac_address, role, group)

    #########################
    # ## PROVISION SPINE1  ###
    #########################
    name = 'spine1-top'
    mac_address = '70:72:cf:ae:ab:08'
    role = 'spine'
    group = None

    fab.provision_switch(name, mac_address, role, group)

    # #####################
    # ## CREATE TENANT  ###
    # #####################
    tenant_name = 'tenant_A'
    fab.create_tenant(tenant_name)

    tenant_name = 'tenant_B'
    fab.create_tenant(tenant_name)

    ######################
    # ## CREATE SEGMENT  ###
    ######################

    tenant_name = 'tenant_A'
    vlan_id = '1000'
    segment_name = 'web'
    port_group = 'any'
    interfaces = 'any'
    switch = 'any'
    print 'hhhhhhhhhhhhhhhhhhhh'
    fab.create_segment(tenant_name, segment_name, vlan_id,
                       port_group, interfaces, switch)

    ##############################
    # ## CREATE LOGICAL ROUTER  ###
    ##############################
    '''

    """
    tenant_name = 'tenant_A'
    lr_ip = '10.1.1.1/24'
    segment_name = 'web'
    fab.create_logical_router(tenant_name,segment_name,lr_ip)
    '''

    fab.get_logical_interfaces(tenant_name)
    '''
    ######################
    ### DELETE TENANT  ###
    ######################
    print 'NOW!!!!!!!!!!'
    import time
    time.sleep(8)
    tenant_name = 'tenant_B'
    fab.delete_tenant(tenant_name)

    ######################
    ### DELETE SEGMENT  ###
    ######################
    print 'NOW!!!!!!!!!!'
    #time.sleep(15)
    tenant_name = 'tenant_A'
    segment_name = 'web'
    fab.delete_segment(tenant_name,segment_name)

    #tenant_name = 'tenant_A'
    #segment_name = 'web'
    #fab.delete_logical_router(tenant_name,segment_name)
    '''
    """

if __name__ == '__main__':
    main()
