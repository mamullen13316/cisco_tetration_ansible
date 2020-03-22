# Cisco Tetration Ansible Modules



- [Cisco Tetration Ansible Modules](#cisco-tetration-ansible-modules)
  - [Usage](#usage)
    - [tetration_add_scope](#tetration_add_scope)
        - [Example Playbook (add_scopes.yml):](#example-playbook-add_scopesyml)
    - [tetration_add_scope_from_yaml](#tetration_add_scope_from_yaml)
        - [Example Playbook (scopes_from_yaml.yml):](#example-playbook-scopes_from_yamlyml)
        - [Example YAML Input file (test_scopes.yml)](#example-yaml-input-file-test_scopesyml)
    - [tetration_scopes_to_yaml](#tetration_scopes_to_yaml)
        - [Example Playbook (scopes_to_yaml.yml):](#example-playbook-scopes_to_yamlyml)
    - [tetration_apps_to_yaml](#tetration_apps_to_yaml)
    - [tetration_add_app_from_yaml](#tetration_add_app_from_yaml)
    - [tetration_inventory_filters_to_yaml](#tetration_inventory_filters_to_yaml)
        - [Example Playbook (inventory_filters_to_yaml.yml):](#example-playbook-inventory_filters_to_yamlyml)
    - [tetration_inventory_filters_from_yaml](#tetration_inventory_filters_from_yaml)
        - [Example Playbook (inventory_filters_from_yaml.yml)](#example-playbook-inventory_filters_from_yamlyml)
        - [Example Input YAML File (test_filters.yml)](#example-input-yaml-file-test_filtersyml)
    - [tetration_delete_agent](#tetration_delete_agent)
        - [Example Playbook (delete_agent.yml)](#example-playbook-delete_agentyml)


## Overview
This repo contains several custom Ansible modules for automating tasks in Cisco Tetration using Ansible:

tetration_add_scope - Add Scopes to a Tetration cluster  

tetration_add_scope_from_yaml - Add Scopes from a YAML file  

tetration_scopes_to_yaml - Export Scopes to a YAML file  

tetration_apps_to_yaml - Export all Tetration Application Workspaces to a YAML file  

tetration_add_app_from_yaml - Add one or more Application Workspaces from a YAML file  

tetration_inventory_filters_to_yaml - Export all Tetration Inventory Filters to a YAML file  

tetration_inventory_filters_from_yaml - Create one or more Inventory Filters from a YAML file  

tetration_delete_agent - Delete one or more Tetration agents based on the hostname



##  Usage

### tetration_add_scope

Adds scopes to a Tetration cluster.  Scopes can be specified in the playbook or brought in via group_vars, or other common Ansible variable locations. 

##### Example Playbook (add_scopes.yml):  
  
```
---
- name: Add scopes to Tetration
  hosts: mycompany
  gather_facts: no

  tasks:
 - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Add scope
    tetration_add_scope:
      hostname: '{{ inventory_hostname }}'
      api_key: '{{ API_KEY }}'
      api_secret: '{{ API_SECRET }}'
      scope_name: 'Test'
      parent_scope_name: 'TAAS104 - mycompany'
      filters:
        - {type: 'eq', field: 'address_type', value: 'IPV4'}
        - {type: 'subnet', field: 'ip', value: '30.0.0.0/8'}
      commit: True
      validate_certs: False
    delegate_to: localhost
```
### tetration_add_scope_from_yaml
  
Reads in Scopes from a YAML file and adds them to the Tetration cluster.  

##### Example Playbook (scopes_from_yaml.yml):  
  
```
---
- name: Upload Scopes to Tetration from a YAML file
  hosts: mycompany_pov
  gather_facts: no

  tasks:
  - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Upload Scopes to the cluster from the YAML file
    tetration_add_scope_from_yaml:
      hostname: '{{ inventory_hostname }}'
      api_key: '{{ API_KEY }}'
      api_secret: '{{ API_SECRET }}'
      source: 'test_scopes.yml'
      validate_certs: False
    delegate_to: localhost
```  
##### Example YAML Input file (test_scopes.yml)

```
---
short_name: Test
short_query:
  type: and
  filters:
  - {type: eq, field: address_type, value: IPV4}
  - {type: subnet, field: ip, value: 30.0.0.0/8}
parent_app_scope_name: mycompanyPOV

---
short_name: Testing123
short_query: {type: subnet, field: ip, value: 10.2.2.2/32}
parent_app_scope_name: Test

---
short_name: Testing456
short_query: {type: subnet, field: ip, value: 10.13.3.0/24}
parent_app_scope_name: Test
```
  
### tetration_scopes_to_yaml
  
Exports all Tetration Scopes to a YAML file.  

##### Example Playbook (scopes_to_yaml.yml):

```
---
- name: Download Scopes from Tetration to a YAML file
  hosts: mycompany
  gather_facts: no

  tasks:
  - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Download scopes from the cluster to a YAML file
    tetration_scopes_to_yaml:
      hostname: '{{ inventory_hostname }}'
      api_key: '{{ API_KEY }}'
      api_secret: '{{ API_SECRET }}'
      dest: 'mycompany_scopes.yml'
      validate_certs: False
    delegate_to: localhost
```
### tetration_apps_to_yaml

Export all Application Workspaces to a YAML File.

Example Playbook (apps_to_yaml.yml):
 
```
---
- name: Download App Details from Tetration to a YAML file
  hosts: mycompany
  gather_facts: no

  tasks:
  - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Download all App details from the cluster to a YAML file
    tetration_apps_to_yaml:
      hostname: '{{ inventory_hostname }}'
      api_key: '{{ API_KEY }}'
      api_secret: '{{ API_SECRET }}'
      dest: 'mycompany_apps.yml'
      validate_certs: False
    delegate_to: localhost
```  
### tetration_add_app_from_yaml
Adds one or more Application Workspaces from a specified YAML file.

Example Playbook:  *** This module is a work in progress.  
  

### tetration_inventory_filters_to_yaml
Export all Tetration Inventory Filters to a YAML file.  

##### Example Playbook (inventory_filters_to_yaml.yml):

```
---
- name: Download Scopes from Tetration to a YAML file
  hosts: mycompany
  gather_facts: no

  tasks:
  - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Download scopes from the cluster to a YAML file
    tetration_inventory_filters_to_yaml:
      hostname: '{{ inventory_hostname }}'
      api_key: '{{ API_KEY }}'
      api_secret: '{{ API_SECRET }}'
      dest: 'mycompany_filters.yml'
      validate_certs: False
    delegate_to: localhost
```
### tetration_inventory_filters_from_yaml

Import Inventory Filters into Tetration from a YAML file.

##### Example Playbook (inventory_filters_from_yaml.yml)

```
---
- name: Upload Inventory Filters from a YAML file
  hosts: mycompany_pov
  gather_facts: no

  tasks:
  - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Upload inventory filters to the cluster from a YAML file
    tetration_add_inventory_filters_from_yaml:
      hostname: '{{ inventory_hostname }}'
      api_key: '4aa4f33357834c71bb5869658c2c34f9'
      api_secret: 'e7777b336fce071ebd90845e8b730632f6a8c6c7'
      source: 'mycompany_filters.yml'
      owner_scope_id: '5c476d0a497d4f5f5b1e6d3f'
      validate_certs: False
    delegate_to: localhost
```  
##### Example Input YAML File (test_filters.yml)

```
---
_id: 5c094950497d4f46fa206ce1
id: 5c094950497d4f46fa206ce1
filter_type: UserInventoryFilter
name: Testing_1
description: null
short_query: {type: subnet, field: ip, value: 100.100.100.0/24}
query:
  type: and
  filters:
  - {field: vrf_id, type: eq, value: 104}
  - {field: ip, type: subnet, value: 100.100.100.0/24}
public: false
primary: false
created_at: 1544112464
updated_at: 1544112464
app_scope_id: 5a8dcf26497d4f22ff665f5b
---
_id: 5c094950497d4f46fa206ce1
id: 5c094950497d4f46fa206ce1
filter_type: UserInventoryFilter
name: Testing_2
description: null
short_query: {type: subnet, field: ip, value: 200.200.200.0/24}
query:
  type: and
  filters:
  - {field: vrf_id, type: eq, value: 104}
  - {field: ip, type: subnet, value: 200.200.200.0/24}
public: false
primary: false
created_at: 1544112464
updated_at: 1544112464
app_scope_id: 5a8dcf26497d4f22ff665f5b
```

### tetration_delete_agent
  
Delete specified Tetration agents from the Tetration cluster based on the hostname.

##### Example Playbook (delete_agent.yml)
```
---
- name: Delete an agent from Tetration
  hosts: mycompany_pov
  gather_facts: no

  tasks:
  - name: Get creds from vault
    include_vars: ./creds.yml
    no_log: true

  - name: Delete agent
    tetration_delete_agent:
      hostname: '{{ inventory_hostname }}'
      api_key: '{{ api_key }}'
      api_secret: '{{ api_secret }}'
      agent_hostname: '{{ item }}'
      validate_certs: False
    with_items:
      - c3-pmtgear-e3eca5
      - c3-pmtgear-ae7273
      - c3-pmtgear-f5206a
      - c3-pmtgear-ea4d3f
      - c3-pmtgear-783fe6
      - c3-pmtgear-354d47
    delegate_to: localhost
```
