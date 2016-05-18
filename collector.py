#
#
#
#

import json
import requests
import _mysql
import logging
import configparser
from models.zabbix import *
from urllib.parse import urlparse
import datetime
from jinja2 import Template, Environment, FileSystemLoader
import os

class Trigger:
    pass

zabbix_status_template = 'zabbix_status.html'

def dequote(s):
    """
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s

# read config file
config = configparser.ConfigParser()
config.read('config.ini')

# configure logging
logfile = dequote(config['default']['logfile'])
loglevel = "logging." + dequote(config['default']['loglevel'])
logging.basicConfig(filename=logfile, level=eval(loglevel), format='%(asctime)s %(message)s')

# create list of zabbix servers configuration
zbx_server_list = []
for section in config.sections():
    if section == 'default':
        continue

    zbx_server_list.append(ZabbixServer(dequote(section),
                                        dequote(config[section]['url']),
                                        dequote(config[section]['username']),
                                        dequote(config[section]['password']))
                           )

trigger_list = []
# get all active triggers and write it to the database
for zbx_server in zbx_server_list:
    zbx_server.login()
    response_trigger_list = zbx_server.trigger_get().json()

    if response_trigger_list['result']:
        for trigger_json in response_trigger_list['result']:
            hostname_json = zbx_server.get_hostname_by_id(trigger_json['hosts'][0]['hostid'])
            hostname = hostname_json.json()['result'][0]['host']

            date = datetime.datetime.fromtimestamp(int(trigger_json['lastchange'])).strftime('%Y-%m-%d %H:%M:%S')

            trigger = Trigger()
            trigger.zabbix_server = zbx_server.name
            trigger.hostname = hostname
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
            if int(trigger_json['priority']) < 6 :
                trigger.severity = "danger"
            if int(trigger_json['priority']) < 4:
                trigger.severity = "warning"
            if int(trigger_json['priority']) < 2:
                trigger.severity = "info"

            trigger.description = trigger_json['description']
            trigger.lastchange = date
            trigger_list.append(trigger)

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(THIS_DIR),
                  trim_blocks=True)
template = env.get_template(zabbix_status_template)

f = open(dequote(config['default']['status_page']), 'w')
f.write(template.render(trigger_list=trigger_list))
f.close()