# Server Settings

## Overview

This guide will walk you through configuring server settings for PokeAlarm.

* [Prerequisites](#prerequisites)
* [Server Settings](#server-settings)
* [Command Line](#command-line)
* [Configuration File](#configuration-file)

## Prerequisites

This guide assumes the following:

1. You have correctly [installed PokeAlarm](installation).

2. You are using Notepad++, Nano, or Vi(m) to configure any files. Do **NOT**
use or open any files with Notepad or TextEdit - they will break your files!

## Server Settings

Settings for the PokeAlarm server can be done the following two ways:

1. **Command Line** - When starting PokeAlarm, you can specify certain settings
with flags following the start up command. For example, you can change the IP
that PokeAlarm binds itself to by using either `python start_pokealarm.py -H
192.168.0.1` or `python start_pokealarm.py --host 192.168.0.1`.  
  **Note**: when used together, command line flags will override arguments
  specified in the configuration file.

2. **Configuration File** - You can also use a configuration file in `ini`
format to set server settings for PokeAlarm. These settings use the same flags
at the command line. For example, you either `host: 192.168.0.1` or
`H: 192.168.0.1` line to the configuration file to change the IP that PokeAlarm
binds itself to.

For files, all relative paths will being from the PokeAlarm root folder, but
absolute file paths can still be used.

## Command Line

To get the most recent command line settings for your version, use the
following command:  `python start_pokealarm.py --help`.

```
usage: start_pokealarm.py [-h] [-cf CONFIG] [-d] [-H HOST] [-P PORT]
                          [-C CONCURRENCY] [-m MANAGER_COUNT] [-M MANAGER_NAME]
                          [-k KEY] [-f FILTERS] [-a ALARMS] [-r RULES]
                          [-gf GEOFENCES] [-l LOCATION] [-L {de,en,es,fr,it,ko,pt,zh_hk}]
                          [-u {metric,imperial}] [-ct {mem,file}] [-tl TIMELIMIT]
                          [-ma MAX_ATTEMPTS] [-tz TIMEZONE]

optional arguments:
  -h, --help            Show this help message and exit.
  -cf CONFIG, --config CONFIG
                        Configuration file.
  -d, --debug           Debug Mode.
  -H HOST, --host HOST  Set web server listening host
  -P PORT, --port PORT  Set web server listening port
  -C CONCURRENCY, --concurrency CONCURRENCY
                        Maximum concurrent connections for the webserver.
  -m MANAGER_COUNT, --manager_count MANAGER_COUNT
                        Number of Manager processes to start.
  -M MANAGER_NAME, --manager_name MANAGER_NAME
                        Names of Manager processes to start.
  -k KEY, --key KEY     Specify a Google API Key to use.
  -f FILTERS, --filters FILTERS
                        Filters configuration file. default: filters.json
  -a ALARMS, --alarms ALARMS
                        Alarms configuration file. default: alarms.json
  -r RULES, --rules     Rules configuration file.
  -gf GEOFENCES, --geofences GEOFENCES
                        Alarms configuration file. default: None
  -l LOCATION, --location LOCATION
                        Location, can be an address or coordinates
  -L {de,en,es,fr,it,ko,pt,zh_hk}, --locale {de,en,es,fr,it,ko,pt,zh_hk}
                        Locale for Pokemon and Move names: default en, check
                        locale folder for more options
  -u {metric,imperial}, --units {metric,imperial}
                        Specify either metric or imperial units to use for
                        distance measurements.
  -ct {mem,file}, --cache_type {mem,file}
                        Caching method used to cache data objects for use in Alerts.
  -tl TIMELIMIT, --timelimit TIMELIMIT
                        Minimum number of seconds remaining on a pokemon to
                        send a notify
  -ma MAX_ATTEMPTS, --max_attempts MAX_ATTEMPTS
                        Maximum number of attempts an alarm makes to send a
                        notification.
  -tz TIMEZONE, --timezone TIMEZONE
                        Timezone used for notifications. Ex:
                        "America/Los_Angeles"
```

## Configuration File

A copy of the most recent configuration file should be located at
`config/config.ini.example`. You can copy this file as a starting point.

By default, PokeAlarm will load the file at `config/config.ini` if it exists.
You can manually specify a configuration file with either the `-cf` or
`--config` file via the command line.

```ini
# Copy this file to config.ini and modify to suit your needs
# Uncomment a line (remove the #) when you want to change its default value.
# Multiple arguments can be listed as [arg1, arg2, ... ]
# Number of arguments must match manager_count or be a single argument (single arguments will apply to all Managers)
# To exclude an argument for a specific manager, use 'None'

# Server Settings
#debug						# Enables debugging mode
#host:						# Address to listen on (default 127.0.0.1)
#port:						# Port to listen on (default: 4000)
#concurrency: 200                               # Maximum concurrent connections for the webserver(default: 200)
#manager_count: 1				# Number of Managers to run. (default: 1)

# Manager-Specific Settings
#manager_name					# Name of the Manager in the logs. Default(manager_0).
#key:						# Google Maps API Key to use
#filters:					# File containing filter rules (default: filters.json)
#alarms:					# File containing alarm rules (default: alarms.json)
#rules: 										# File containing rules settings (default: None)
#geofence:					# File containing geofence(s) used to filter (default: None)
#location:					# Location for the manager. 'Name' or 'lat lng' (default: None)
#locale:					# Language to be used to translate names (default: en)
#cache_type:					# Method used to cache dynamic objects used in Alerts. (default: mem)
#unit:						# Units used to measure distance. Either 'imperial' or 'metric' (default: imperial)
#timelimit:					# Minimum number of seconds remaining to send a notification (default: 0)
#max_attempts:					# Maximum number of attempts an alarm makes to send a notification. (default: 3)
#timezone:					# Timezone used for notifications Ex: 'America/Los_Angeles' or '[America/Los_Angeles, America/New_York]'
```
