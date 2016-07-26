# zabbifier-web

Simple script that collects all active triggers from several zabbix servers.

# Setup

1. clone the repository

2. cp config.ini.sample config.ini. Edit config.ini

3. Configure web server to service status_page (see config.ini)

4. Setup cron job:
```
*/2 * * * *     (cd /path/to/zabbifier-web && /usr/bin/python collector.py) &>/dev/null
```