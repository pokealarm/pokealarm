# Server Settings

## Overview

This guide will walk you through configuring server settings for PokeAlarm.

* [Prerequisites](#prerequisites)
* [Server Settings](#server-settings)
* [Command Line](#command-line)
* [Configuration File](#configuration-file)

## Prerequisites

This guide assumes the following:

1. You have correctly [installed PokeAlarm](../getting-started/installation.html).

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
usage: start_pokealarm.py [-h] [-cf CONFIG] [-H HOST] [-P PORT]
                          [-C CONCURRENCY] [-d] [-q] [-ll {1,2,3,4,5}]
                          [-lf LOG_FILE] [-ls LOG_SIZE] [-lc LOG_CT]
                          [-m MANAGER_COUNT] [-M MANAGER_NAME]
                          [-mll {1,2,3,4,5}] [-mlf MGR_LOG_FILE]
                          [-mls MGR_LOG_SIZE] [-mlc MGR_LOG_CT] [-f FILTERS]
                          [-a ALARMS] [-r RULES] [-gf GEOFENCES] [-l LOCATION]
                          [-L {de,en,es,fr,it,ko,pt,zh_hk}]
                          [-u {metric,imperial}] [-tz TIMEZONE] [-k GMAPS_KEY]
                          [--gmaps-rev-geocode GMAPS_REV_GEOCODE]
                          [--gmaps-dm-walk GMAPS_DM_WALK]
                          [--gmaps-dm-bike GMAPS_DM_BIKE]
                          [--gmaps-dm-drive GMAPS_DM_DRIVE]
                          [--gmaps-dm-transit GMAPS_DM_TRANSIT]
                          [-ct {mem,file}] [-tl TIMELIMIT] [-ma MAX_ATTEMPTS]

optional arguments:
  -h, --help            show this help message and exit
  -cf CONFIG, --config CONFIG
                        Configuration file
  -H HOST, --host HOST  Set web server listening host
  -P PORT, --port PORT  Set web server listening port
  -C CONCURRENCY, --concurrency CONCURRENCY
                        Maximum concurrent connections for the webserver.
  -d, --debug           Enable debuging mode.
  -q, --quiet           Disables output to console.
  -ll {1,2,3,4,5}, --log-lvl {1,2,3,4,5}
                        Verbosity of the root logger.
  -lf LOG_FILE, --log-file LOG_FILE
                        Path of a file to attach to a manager's logger.
  -ls LOG_SIZE, --log-size LOG_SIZE
                        Maximum size in mb of a log before rollover.
  -lc LOG_CT, --log-ct LOG_CT
                        Maximum number of logs to keep.
  -m MANAGER_COUNT, --manager_count MANAGER_COUNT
                        Number of Manager processes to start.
  -M MANAGER_NAME, --manager_name MANAGER_NAME
                        Names of Manager processes to start.
  -mll {1,2,3,4,5}, --mgr-log-lvl {1,2,3,4,5}
                        Set the verbosity of a manager's logger.
  -mlf MGR_LOG_FILE, --mgr-log-file MGR_LOG_FILE
                        Path of a file to attach to a manager's logger.
  -mls MGR_LOG_SIZE, --mgr-log-size MGR_LOG_SIZE
                        Maximum megabytes of a manager's log before rollover.
  -mlc MGR_LOG_CT, --mgr-log-ct MGR_LOG_CT
                        Maximum number of old manager's logs to keep before
                        deletion.
  -f FILTERS, --filters FILTERS
                        Filters configuration file. default: filters.json
  -a ALARMS, --alarms ALARMS
                        Alarms configuration file. default: alarms.json
  -r RULES, --rules RULES
                        Rules configuration file. default: None
  -gf GEOFENCES, --geofences GEOFENCES
                        Alarms configuration file. default: None
  -l LOCATION, --location LOCATION
                        Location, can be an address or coordinates
  -L {de,en,es,fr,it,ko,pt,zh_hk}, --locale {de,en,es,fr,it,ko,pt,zh_hk}
                        Locale for Pokemon and Move names: default en," + "
                        check locale folder for more options
  -u {metric,imperial}, --units {metric,imperial}
                        Specify either metric or imperial units to use for
                        distance " + "measurements.
  -tz TIMEZONE, --timezone TIMEZONE
                        Timezone used for notifications. Ex:
                        "America/Los_Angeles"
  -k GMAPS_KEY, --gmaps-key GMAPS_KEY
                        Specify a Google API Key to use.
  --gmaps-rev-geocode GMAPS_REV_GEOCODE
                        Enable Walking Distance Matrix DTS.
  --gmaps-dm-walk GMAPS_DM_WALK
                        Enable Walking Distance Matrix DTS.
  --gmaps-dm-bike GMAPS_DM_BIKE
                        Enable Bicycling Distance Matrix DTS.
  --gmaps-dm-drive GMAPS_DM_DRIVE
                        Enable Driving Distance Matrix DTS.
  --gmaps-dm-transit GMAPS_DM_TRANSIT
                        Enable Transit Distance Matrix DTS.
  -ct {mem,file}, --cache_type {mem,file}
                        Specify the type of cache to use. Options: ['mem',
                        'file'] (Default: 'mem')
  -tl TIMELIMIT, --timelimit TIMELIMIT
                        Minimum limit
  -ma MAX_ATTEMPTS, --max_attempts MAX_ATTEMPTS
                        Maximum attempts an alarm makes to send a
                        notification.
```

## Configuration File

A copy of the most recent configuration file should be located at
`config/config.ini.example`. You can copy this file as a starting point.

By default, PokeAlarm will load the file at `config/config.ini` if it exists.
You can manually specify a configuration file with either the `-cf` or
`--config` file via the command line.

```ini
# DO NOT USE NOTEPAD OR TEXTEDIT TO EDIT FILES!
# USE AN EDITOR SUCH AS NOTPAD++, ATOM, NANO OR VI(M)
# You can create a copy of this config and edit it to suit your needs.
# Uncomment a line (remove the #) when you want to change its default value.
# By default, PA will use `config/config.ini` to load settings.
# You can override the config file selection with `--config-file` or `-cf`.


########################
# Webserver Settings
########################

#host: 127.0.0.1                # Interface to listen on (default='127.0.0.1')
#port: 4000						# Port to listen on (default='4000')
#concurrency: 200               # Maximum concurrent connections to webserver (default=200)
#manager_count: 1				# Number of Managers to run (default=1)
#debug                          # Enable debug logging (default='False)
#quiet                          # Disable output to stdin/stdout.
#log-lvl: 3                     # Verbosity of the main logger (default=3)
#log-file: logs/pokealarm.log   # File path of the main logger (default='logs/pokealam.log')
#log-size: 100                  # Maximum size in mb of a log before rollover.
#log-ct: 5                      # Maximum number of logs to keep.


#########################
# Manager Settings
#########################
# All of the settings below this line are manager-specific.
# If a single setting is supplied, it will apply to all Managers.
# Example: `locale: en` will set all Managers to english
# If an array of settings is supplied, they will be apply to Managers in order.
# Example: `locale: [ en, fr, en ]` sets a different language for 3 Managers.
# `None` can be used to exempt a Manager from an optional setting

#manager_name:                  # Name of Manager, used for logging (default='manager#')

# Logging Settings
#####################
#mgr-log-lvl: 3                 # Verbosity of a manager's logger (default=3)
#mgr-log-file: logs/mgr.log     # Path of a file to attach to a manager's logger.
#mgr-log-size: 100              # Maximum size (in mb) of a log before rollover.
#mgr-log-ct: 5                  # Maximum number of older logs to keep.


# File Settings
#####################
# File settings define location of files with settings for a Manager.
# Relative paths are presumed from install folder, root paths are absolute.

#filters: filters.json          # Filters for the Manager (default='filters.json')
#alarms: alarms.json            # Alarms for the Manager (default='alarms.json')
#rules: rules.json              # Rules for the Manager (default=None)
#geofence: geofence.txt         # Geofences to be used in Filters (default=None)


# Location Specific
#####################
#location:                       # Location, as address or coordinates (default=None)
#locale: en                     # Language used for DTS translations (default='en')
                                # Options: ['de', 'en', 'es', 'fr', 'it', 'ko', 'pt', 'zh_hk' ]
#unit: imperial                 # Units used to measurements.(default='imperial')
                                # Options: ['imperial', 'metric' ]
#timezone: America/Los_Angeles  # Timezones used for notifications. Default uses system time (default=None)
                                # Options: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones


# GMaps Settings
################
#gmaps-key:                     # Google Maps API Key (default=None)
#gmaps-rev-geocode: yes         # Enable Reverse Geocoded DTS. (default='no')
                                # Note: This requires the Reverse Geocoding API to be enabled on your GMAPs key.
#gmaps-dm-walk: yes             # Enable Walking DM DTS. (default='no')
                                # Note: This requires the Distance Matrix API to be enabled on your GMAPs key.
#gmaps-dm-bike: yes             # Enable Bicycling DM DTS. (default='no')
                                # Note: This requires the Distance Matrix API to be enabled on your GMAPs key.
#gmaps-dm-drive: yes            # Enable Driving DM DTS. (default='no')
                                # Note: This requires the Distance Matrix API to be enabled on your GMAPs key.
#gmaps-dm-transit: yes          # Enable Transit DM DTS. (default='no')
                                # Note: This requires the Distance Matrix API to be enabled on your GMAPs key.


# Miscellaneous
################
#cache_type: file               # Type of cache used to share information between webhooks. (default='mem')
                                # Options: ['mem', 'file']
#timelimit: 0					# Minimum seconds remaining on an Event to trigger notification (default=0)
# Note - `max_attempts` is being deprecated and may be replaced by alarm-level settings
#max_attempts: 3				# Maximum number of attempts an alarm makes to send a notification. (default=3)
```
