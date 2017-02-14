# zabbifier-web

A simple script that collects all active triggers from several zabbix servers.

# Setup

1. clone the repository

2. cp config.ini.sample config.ini. Edit config.ini

3. Configure a web server to service the status_page (see config.ini)

4. Setup a cron job:
```
*/2 * * * *     (cd /path/to/zabbifier-web && /usr/bin/python collector.py) &>/dev/null
```
