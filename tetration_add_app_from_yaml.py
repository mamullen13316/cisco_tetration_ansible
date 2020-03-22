#!/usr/bin/python

DOCUMENTATION = '''
---
module: tetration_add_app_from_yaml
author: Matt Mullen
version_added: "1.0"
short_description: Import App Workspaces to a Tetration cluster from a file in YAML format
description:
    - Connects to a specified Tetration cluster and imports App Workspaces from a file in YAML format

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
            - The YAML file to import the App Workspaces from

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
def ScopeLookup(scopes,name):
    for scope in scopes:
        if scope['short_name'] == name:
            return scope['id']


def app_upload(hostname,api_key,api_secret,source,validate_certs):
    result = {"ansible_facts": {'result':[]}}
    api_endpoint = 'https://{0}'.format(hostname)
    restclient = RestClient(api_endpoint, api_key=api_key, api_secret=api_secret, verify=validate_certs)

    app_list = []
    with open(source, 'r') as f:
        for data in oyaml.load_all(f):
            app_list.append(data)

    for i, app in enumerate(app_list):
        exists = False
        if scope['parent_app_scope_name']:
            resp = restclient.get('/openapi/v1/app_scopes')
            if not resp.status_code == 200:
                return (1, "Error {0}: {1} during connection attempt to {2}/openapi/v1/app_scopes. \n".format(
                    resp.status_code,
                    resp.reason, api_endpoint))
            current_scopes = json.loads(resp.content)
            for current_scope in current_scopes:
                if current_scope['short_name'] == scope['short_name']:
                    exists = True
            if not exists:
                scope['parent_app_scope_id'] = ParentIDLookup(current_scopes,scope['parent_app_scope_name'])
                scope.pop('parent_app_scope_name')
                print('Posting scope {0} to the cluster'.format(scope['short_name']))
                resp = restclient.post('/openapi/v1/app_scopes', json_body=json.dumps(scope))
                if not resp.status_code == 200:
                    return (1, "Error {0}: {1} creating scope {2}. \n{3}".format(
                        resp.status_code,
                        resp.reason,
                        scope['short_name'],
                        resp.json()))
                result['ansible_facts']['result'].append(resp.json())

    if result['ansible_facts']['result']:
        result['changed'] = True
    else:
        result['changed'] = False
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
            validate_certs=dict(required=False, type=bool, default=True)
    ))

    code, response = app_upload(module.params["hostname"],
                                   module.params["api_key"],
                                   module.params["api_secret"],
                                   module.params["source"],
                                   module.params["validate_certs"])
    if code == 1:
        module.fail_json(msg=response)
    else:
        module.exit_json(**response)

    return code


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()