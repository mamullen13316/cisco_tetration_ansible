#!/usr/bin/python

DOCUMENTATION = '''
---
module: tetration_delete_agent.py
author: Matt Mullen
version_added: "1.0"
short_description: Delete an agent from the Tetration cluster
description:
    - Deletes an agent from the cluster.  Intended to be used after a host is de-commissioned.  

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
    agent_hostname:
        description:
            - The hostname of the agent to be deleted
    validate_certs:
        description:
            - Boolean to turn on or off certificate validation

'''
EXAMPLES = '''
---
- name: Delete agent from Tetration
  hosts: mycompany
  gather_facts: no

  tasks:
  - name: Delete agent
    tetration_delete_agent:
      hostname: '{{ inventory_hostname }}'
      api_key: '0b426d1a632747b08b4075379d9f484b'
      api_secret: 'ce53f00f2d5a61b08598c108c824696b45f96bca'
      agent_hostname: 'win10-1'
      validate_certs: False
    delegate_to: localhost
 
'''
from tetpyclient import RestClient
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests

#Disable insecure request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ---------------------------------------------------------------------------
# Delete agent
# ---------------------------------------------------------------------------

def delete_agent(hostname, api_key, api_secret, agent_hostname, validate_certs):
    result = {"ansible_facts": {}}
    api_endpoint = 'https://{0}'.format(hostname)
    restclient = RestClient(api_endpoint, api_key=api_key, api_secret=api_secret, verify=validate_certs)
# Getting the sensors to do sensor_id lookup based on the hostname
    resp = restclient.get('/openapi/v1/sensors')
    if not resp.status_code == 200:
        return (1, "Error {0}: {1} during connection attempt to {2}/openapi/v1/sensors. \n".format(resp.status_code,
                                                                              resp.reason,api_endpoint))
    sensor_list = json.loads(resp.content)
# Look up sensor id based on hostname
    uuid = get_sensor_id(agent_hostname,sensor_list)
    if uuid:
        resp = restclient.delete('/openapi/v1/sensors/{0}'.format(uuid))
        if not resp.status_code == 204:
            return (
            1, "Error {0}: {1} during connection attempt to {2}/openapi/v1/sensors/{3}. \n".format(resp.status_code,
                                                                                                  resp.reason,
                                                                                                  api_endpoint,
                                                                                                   uuid))
    else:
        return (1, "No agent was found with hostname: {0}".format(agent_hostname))

    result["ansible_facts"] = {}
    result['changed'] = True
    return (0, result)

# Sensor lookup uuid by name function
def get_sensor_id(hostname, sensor_list):
    for payload in sensor_list['results']:
        if payload['host_name'] == hostname:
            uuid = payload['uuid']
            return uuid


#---------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True),
            api_key=dict(required=True),
            api_secret=dict(required=True),
            agent_hostname=dict(required=True),
            validate_certs=dict(required=False, type=bool, default=True)
    ))

    code, response = delete_agent(module.params["hostname"],
                                   module.params["api_key"],
                                   module.params["api_secret"],
                                   module.params["agent_hostname"],
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

