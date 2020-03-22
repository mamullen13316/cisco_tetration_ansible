#!/usr/bin/python

DOCUMENTATION = '''
---
module: tetration_add_inventory_filters_from_yaml
author: Matt Mullen
version_added: "1.0"
short_description: Load Inventory Filters from a YAML file and create on Tetration cluster
description:
    - imports Inventory Filters in a specified YAML file into the Tetration cluster

requirements:
    - tetpyclient 
options:
    hostname:
        description:
            - The hostname or IP address of the Tetration cluster
    api_key:
        description:
            - The api key to use for the connection.  This must be created on the Tetration cluster.
        required: true
    api_secret:
        description:
            - The api secret to use for the connection.  This must be created on the Tetration cluster.
    source:
        description:
            - The YAML file to import 

'''

from tetpyclient import RestClient
import json
import oyaml
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests

#Disable insecure request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Functions to upload Scopes from YAML file to the cluster
# ---------------------------------------------------------------------------

def upload(hostname,api_key,api_secret,source,validate_certs,owner_scope_id):
    result = {"ansible_facts": {}}
    api_endpoint = 'https://{0}'.format(hostname)
    restclient = RestClient(api_endpoint, api_key=api_key, api_secret=api_secret, verify=validate_certs)
    filter_list = []
    with open(source, 'r') as f:
        for data in oyaml.load_all(f):
            filter_list.append(data)

    for filter in filter_list:
        filter['app_scope_id'] = owner_scope_id
        filter.pop('id')
        filter.pop('_id')
        resp = restclient.post('/openapi/v1/filters/inventories', json_body=json.dumps(filter))

        if not resp.status_code == 200:
            return (1, "Error {0}: {1} during connection attempt to {2}/openapi/v1/filters/inventories. \n{3}".format(resp.status_code,
                                                                               resp.reason,api_endpoint,resp.json()))
    result['changed'] = True
    return (0, result)

#---------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True),
            api_key=dict(required=True),
            api_secret=dict(required=True),
            source=dict(required=True),
            validate_certs=dict(required=False, type=bool, default=True),
            owner_scope_id=dict(required=True)
    ))

    code, response = upload(module.params["hostname"],
                                   module.params["api_key"],
                                   module.params["api_secret"],
                                   module.params["source"],
                                   module.params["validate_certs"],
                                   module.params["owner_scope_id"])
    if code == 1:
        module.fail_json(msg=response)
    else:
        module.exit_json(**response)

    return code


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()