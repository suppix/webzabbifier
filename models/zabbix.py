#
#
#
#

import json
import requests
import logging

class ZabbixServer:
    def __init__(self, name, url, username, password):
        self.name = name
        self.url = url
        self.username = username
        self.password = password

        self.user_login_json = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.password,
            },
            "id": 1,
        }

        self.trigger_get_json = {
            "jsonrpc": "2.0",
            "method": "trigger.get",
            "params": {
                "output": "extend",
                "monitored": "1",
                "filter": {"value": "1"},
                "selectHosts": "1",
                "expandData": "1",
                "expandComment": "1",
                "expandDescription": "1",
                "expandExpression": "1",
            },
            "id": 2,
            "auth": None
        }

        self.host_get_json = {
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
                "hostids": None,
            },
            "auth": None,
            "id": 2,
        }

    def login(self):
        response = self.do_zbx_request(self.user_login_json)

        self.trigger_get_json['auth'] = response.json()['result']
        self.host_get_json['auth'] = response.json()['result']

    def trigger_get (self):
        response = self.do_zbx_request(self.trigger_get_json)

        return response

    def get_hostname_by_id(self, hostid):
        self.host_get_json['params']['hostids'] = str(hostid)
        response = self.do_zbx_request(self.host_get_json)

        return response

    def do_zbx_request(self, request: object) -> object:
        data_json = json.dumps(request)
        headers = {'content-type': 'application/json'}
        response = requests.post(self.url + '/api_jsonrpc.php',
                                 data=data_json,
                                 headers=headers,
                                 auth=(self.username, self.password),
                                 verify=False)

        if response != None:
            response_json = response.json()
        else:
            logging.warning('Error performing request: %s, %s', response.status_code, response.text)

        if 'error' in response_json:
            logging.warning('Error performing request %s', response_json['error'])

        return response