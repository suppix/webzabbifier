#
#
#
#

from models.zabbix import *
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os
from dateutil.tz import tzlocal

zbx_status_template = 'zabbix_status.html'
config_filename = "config.ini"

# parse config file
from configobj import ConfigObj
config = ConfigObj(config_filename)

# configure logging
logfile = config['default']['logfile']
loglevel = "logging." + config['default']['loglevel']
logging.basicConfig(filename=logfile, level=eval(loglevel), format='%(asctime)s %(message)s')

# create list of zabbix servers configuration from config sections
zbx_server_list = []
for section in config.keys():
    if section == 'default':
        continue

    zbx_server_list.append(ZabbixServer(section,
                                        config[section]['url'],
                                        config[section]['username'],
                                        config[section]['password'])
                           )

trigger_list = []
# get all active triggers
for zbx_server in zbx_server_list:
    zbx_server.login()
    trigger_list.extend(zbx_server.trigger_get())

# write all active triggers to the html status page
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
env = Environment(loader=FileSystemLoader(THIS_DIR),
                            trim_blocks=True)
template = env.get_template(zbx_status_template)

f = open(config['default']['status_page'], 'w')
f.write(template.render(trigger_list=trigger_list, date=datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M %Z")))
f.close()