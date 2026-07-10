#!/usr/bin/env python3
"""
Ansible Dynamic Inventory Script
Reads hosts definition from hosts.json and outputs Ansible JSON format.
"""

import os
import sys
import json
import argparse

class ExampleInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Load inventory from JSON database
        self.load_inventory_data()

        if self.args.list:
            print(json.dumps(self.inventory, indent=2))
        elif self.args.host:
            # Return host variables
            hostvars = self.inventory.get('_meta', {}).get('hostvars', {}).get(self.args.host, {})
            print(json.dumps(hostvars, indent=2))
        else:
            print(json.dumps({'error': 'Specify --list or --host <hostname>'}, indent=2))
            sys.exit(1)

    def load_inventory_data(self):
        # Determine path to hosts.json relative to this script
        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_path = os.path.join(dir_path, 'hosts.json')

        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            self.inventory = data
        except Exception as e:
            # Fallback mock data in case of error reading file
            self.inventory = {
                "k8s_master": {"hosts": ["dynamic-master-01"]},
                "k8s_worker": {"hosts": ["dynamic-worker-01"]},
                "k8s_cluster": {
                    "children": ["k8s_master", "k8s_worker"]
                },
                "_meta": {
                    "hostvars": {
                        "dynamic-master-01": {"ansible_host": "192.168.100.11", "ansible_user": "deploy"},
                        "dynamic-worker-01": {"ansible_host": "192.168.100.12", "ansible_user": "deploy"}
                    }
                }
            }

    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true')
        parser.add_argument('--host', action='store')
        self.args = parser.parse_args()

if __name__ == '__main__':
    ExampleInventory()
