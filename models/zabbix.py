#
#
#
#

import json
import requests
import logging
from datetime import datetime
from utils import human_readable_date
import dateutil.relativedelta
import time

# disable InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Trigger:
    pass

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

        # handle login errors

        self.trigger_get_json['auth'] = response.json()['result']
        self.host_get_json['auth'] = response.json()['result']

        # return true or false

    def trigger_get (self):
        trigger_list_json = self.do_zbx_request(self.trigger_get_json).json()
        trigger_list=[]

        if trigger_list_json['result']:
            for trigger_json in trigger_list_json['result']:
                hostname = self.get_hostname_by_id(trigger_json['hosts'][0]['hostid'])

                date = datetime.fromtimestamp(int(trigger_json['lastchange'])).strftime('%Y-%m-%d %H:%M:%S')

                trigger = Trigger()
                trigger.server_hostname = self.name
                trigger.agent_hostname = hostname
                """
                https://www.zabbix.com/documentation/3.0/manual/api/reference/trigger/object
                0 - (default)
                not classified;
                1 - information;
                2 - warning;
                3 - average;
                4 - high;
                5 - disaster.
                """
                if int(trigger_json['priority']) < 6:
                    trigger.severity = "danger"
                if int(trigger_json['priority']) < 4:
                    trigger.severity = "warning"
                if int(trigger_json['priority']) < 2:
                    trigger.severity = "info"

                trigger.description = trigger_json['description']
                trigger.lastchange = date

                # calculate age of the trigger
                dt1 = datetime.fromtimestamp(int(trigger_json['lastchange']))
                dt2 = datetime.fromtimestamp(time.time())
                rd = dateutil.relativedelta.relativedelta(dt2, dt1)

                trigger.age = human_readable_date(rd)

                trigger_list.append(trigger)

        return trigger_list

    def get_hostname_by_id(self, hostid):
        self.host_get_json['params']['hostids'] = str(hostid)
        response = self.do_zbx_request(self.host_get_json)

        return response.json()['result'][0]['host']

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