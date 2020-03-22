#!/usr/bin/python

DOCUMENTATION = '''
---
module: tetration_add_scope.py
author: Matt Mullen
version_added: "1.0"
short_description: Create/Update Scopes on a Tetration cluster
description:
    - Creates a Scope and associated query on a Tetration cluster,  or updates an existing Scope if already present

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
    scope_name:
        description:
            - The target Scope name
    filters:
        description:
            - A list of filters in the format {type: [TYPE], field: [FIELD_NAME], value: 'IPV4'}
            Valid values for TYPE:  eq, neq, contains, subnet  *** ADDITIONAL TBD
            Valid values for FIELD_NAME: address_type, ip  *** ADDITIONAL TBD

    parent_scope_name:
        description:
            - Name of the parent scope that the specified scope_name should be created under
    commit:
        description:
            - When set to True,  commits the changes to the scope queries
    validate_certs:
        description:
            - When set to False, disables certificate verification (default = True)

'''
EXAMPLES = '''
---
- name: Add scopes to Tetration
  hosts: mycompany
  gather_facts: no

  tasks:
  - name: Add scope
    tetration_add_scope:
      hostname: '{{ inventory_hostname }}'
      api_key: '0b426d1b542747b08b4075379d9f484b'
      api_secret: 'ce53f00f2d6aa1b08398c108c824696b45f96bca'
      scope_name: 'Test'
      parent_scope_name: 'TAAS104 - mycompany'
      filters:
        - {type: 'eq', field: 'address_type', value: 'IPV4'}
        - {type: 'subnet', field: 'ip', value: '30.0.0.0/8'}
      commit: True
      validate_certs: False
    delegate_to: localhost
 
'''
from tetpyclient import RestClient
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

#Disable insecure request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Create or modify scopes
# ---------------------------------------------------------------------------

def scope_action(hostname, api_key, api_secret, scope_name, filters, parent_scope_name, commit, validate_certs):
    result = {"ansible_facts": {}}
    api_endpoint = 'https://{0}'.format(hostname)
    restclient = RestClient(api_endpoint, api_key=api_key, api_secret=api_secret, verify=validate_certs)
# Getting the scopes to do parent_id lookup and check if scope already exists
    resp = restclient.get('/openapi/v1/app_scopes')
    if not resp.status_code == 200:
        return (1, "Error {0}: {1} during connection attempt to {2}/openapi/v1/app_scopes. \n".format(resp.status_code,
                                                                              resp.reason,api_endpoint))
    cluster_scopes = json.loads(resp.content)

# De-capitalize and hyphenate any field keywords in the filters
    for i, filter in enumerate(filters):
        if filter['field'] == 'Address Type':
            newfield = filter['field'].lower().replace(' ', '_')
            filters[i]['field'] = newfield
        if filter['field'] == 'Address':
            filters[i]['field'] = 'ip'
            filters[i]['type'] = 'subnet'

# Check if scope exists, and filter is the same
    for scope in cluster_scopes:
        if scope_name == scope['short_name'] and scope['query']['filters'][1]['filters'] == filters:
            result['changed'] = False
            return (0, result)

#Parent ID lookup
    cluster_scope_dict = {x['short_name']: x['id'] for x in cluster_scopes}
    for cluster_scope in cluster_scope_dict.keys():
        if cluster_scope == parent_scope_name:
            parent_scope_id = cluster_scope_dict[cluster_scope]


#Build the json payload
    payload = json.dumps(dict(short_name=scope_name,
               short_query=dict(type='and',
                                filters=filters),
                              parent_app_scope_id=parent_scope_id))


#If scope already present on the cluster do a PUT, otherwise POST
    if scope_name in cluster_scope_dict:
        resp = restclient.put('/openapi/v1/app_scopes/{0}'.format(cluster_scope_dict[scope_name]),json_body=payload)
    else:
        resp = restclient.post('/openapi/v1/app_scopes',json_body=payload)

    if not resp.status_code == 200:
        return (1, "Error {0}: {1} posting scope to the cluster. \n{2}".format(resp.status_code,
                                                                                   resp.reason,
                                                                               resp.json()))

#If commit flag set,  commit the change at the parent scope
    if commit:
        resp = restclient.post('/openapi/v1/app_scopes/commit_dirty?root_app_scope_id={0}'.format(parent_scope_id),
                               json_body=json.dumps({'sync': True}))

        if not resp.status_code == 200:
            return (1, "Error {0}: {1} committing scope query change. \n{2}".format(resp.status_code,
                                                                                   resp.reason,
                                                                                   resp.json()))

    result["ansible_facts"] = resp.json()
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
            scope_name=dict(required=True),
            filters=dict(required=True, type=list),
            parent_scope_name=dict(required=True),
            commit=dict(required=False, type=bool, default=False),
            validate_certs=dict(required=False, type=bool, default=True)
    ))

    code, response = scope_action(module.params["hostname"],
                                   module.params["api_key"],
                                   module.params["api_secret"],
                                   module.params["scope_name"],
                                   module.params["filters"],
                                  module.params["parent_scope_name"],
                                  module.params["commit"],
                                  module.params["validate_certs"])
    if code == 1:
        module.fail_json(msg=response)
    else:
        module.exit_json(**response)

    return code


from ansible.module_utils.basic import AnsibleModule

if __name__ == '__main__':
    main()
#

