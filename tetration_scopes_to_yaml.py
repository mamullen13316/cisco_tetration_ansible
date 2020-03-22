#!/usr/bin/python

DOCUMENTATION = '''
---
module: tetration_scopes_to_yaml
author: Matt Mullen
version_added: "1.0"
short_description: Export scopes on a Tetration cluster to a file in YAML format
description:
    - Connects to a specified Tetration cluster and exports all scopes to a file in YAML format

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
    dest:
        description:
            - The filename to export the Scopes

'''

from tetpyclient import RestClient
import json
import oyaml
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
import os

#Disable insecure request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Functions to download existing Scopes to YAML
# ---------------------------------------------------------------------------
def scope_name_lookup(scopes,id):
    for scope in scopes:
        if scope['id'] == id:
            return scope['short_name']


def scope_download(hostname,api_key,api_secret,dest,validate_certs):
    result = {"ansible_facts": {}}
    api_endpoint = 'https://{0}'.format(hostname)
    restclient = RestClient(api_endpoint, api_key=api_key, api_secret=api_secret, verify=validate_certs)
    resp = restclient.get('/openapi/v1/app_scopes')
    if not resp.status_code == 200:
        return (1, "Error {0}: {1} during connection attempt to {2}/openapi/v1/app_scopes. \n".format(resp.status_code,
                                                                           resp.reason,api_endpoint))
    scopes = json.loads(resp.content)
    shortened_scope_list = []
    for i in range(len(scopes)-1,0,-1):
        shortened_scope_list.append(dict(short_name=scopes[i]['short_name'],
                                         short_query=scopes[i]['short_query'],
                                         parent_app_scope_name=scope_name_lookup(scopes,scopes[i]['parent_app_scope_id'])))
    with open(dest, 'w') as f:
        for scope in shortened_scope_list:
            f.write('---\n')
            oyaml.dump(scope, f, allow_unicode=True, encoding='utf-8')
            f.write('\n')

    result["ansible_facts"] = {'Output':os.path.join(os.getcwd(),dest)}
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
            dest=dict(required=True),
            validate_certs=dict(required=False, type=bool, default=True)
    ))

    code, response = scope_download(module.params["hostname"],
                                   module.params["api_key"],
                                   module.params["api_secret"],
                                   module.params["dest"],
                                   module.params["validate_certs"])
    if code == 1:
        module.fail_json(msg=response)
    else:
        module.exit_json(**response)

    return code


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()