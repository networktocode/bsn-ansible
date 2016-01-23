
This is a collection of Ansible modules for Big Switch products.  There are two modules so far: one to gather *facts* for Big Cloud Fabric and another to gather *facts* for Big Monitoring Fabric.

> Due to API issues for BMF, there are few facts not being gathered.

This is extremely easy to test using Big Switch's online labs: http://labs.bigswitch.com/home.  All you need to do is clone this repository and update the IP address found in the [hosts](hosts) file with the IP of your controller (for BCF, BMF, or both)

The facts gathered can be used as inputs to other modules or used in templates to create documentation used for inventorying, assessments, etc.

* The facts returned for Big Cloud Fabric are returned as a dictionary using the key `bsnbcf`.
* The facts returned for Big Monitoring Fabric are returned as a dictionary using the key `bsnbmf`.


[Example Playbook](bsn.yml):

```yaml
---

   - name: GATHER FACTS FROM BIG SWITCH CONTROLLERS
     hosts: bcf
     connection: local

     tasks:

       - name: GATHER FACTS
         bcf_get_facts: controller={{ controller_ip }} username={{ un }} password={{ pwd }}

       - name: DUMP FACTS TO TERMINAL
         debug: var=bsnbcf


```

Executing Playbook:

```
$ ansible-playbook -i hosts bsn.yml 

PLAY [GATHER FACTS FROM BIG CLOUD FABRIC] ************************************* 

TASK: [GATHER FACTS] ********************************************************** 
ok: [bcf_lab]

TASK: [DUMP FACTS TO TERMINAL] ************************************************ 
ok: [bcf_lab] => {
    "var": {
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

PLAY RECAP ******************************************************************** 
bcf_lab                   : ok=2    changed=0    unreachable=0    failed=0   

```

