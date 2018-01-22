# Remedy's v3 Guide

Updated: 28 August 2017

## Purpose

* This document is intended to quickly provide PokeAlarm users with info to
get started. It is not intended to replace the full wiki.

## Overview

* [Before you begin](#before-you-begin)
* [Notes](#notes)
* [Introduction](#introduction)
  * [Changes to JSON files](#changes-to-json-files)
    * [Config file: `filters.json`](#config-file-filtersjson)
        * [Gyms](#gyms)
        * [Changes in move filtering](#changes-in-move-filtering)
            * [Filtering on a single `quick_move`](#filtering-on-a-single-quick_move)
            * [Filtering on more than one `charge_move`](#filtering-on-multiple-charge_move-moves)
            * [NEW: filtering on `moveset`](#new-filtering-on-moveset)
            * [NEW: filtering on `size`](#new-filtering-on-size)
        * [New: Optional ignoring of pokemon with missing IVs or moves](#new-optional-ignoring-of-pokemon-with-missing-ivs-or-moves)
    * [Config file: `geofence.txt` (optional)](#config-file-geofencetxt-optional)
    * [Config file: `alarms.json`](#config-file-alarmsjson)
        * [New and updated Dynamic Text Substitutions](#new-and-updated-dynamic-text-substitutions)
* [Upgrading from PokeAlarm Version 2 to Version 3](#upgrading-from-pokealarm-version-2-to-version-31)
* [Running PokeAlarm v3](#running-pokealarm-v3)
    * [Optional Arguments for `start_pokealarm.py`](#optional-arguments-for-start_pokealarmpy)
    * [Running multiple alarms, filters, etc., in a single `start_pokealarm.py` instance from the command line](#running-multiple-alarms-filters-etc-in-a-single-start_pokealarmpy-instance-from-the-command-line)
    * [Running one Manager from the command line](#running-one-manager-from-the-command-line)
    * [Running two Managers from the command line](#running-two-managers-from-the-command-line)
    * [Special case: using one `filters.json`, `geofence.txt`, `alarms.json`, etc., for all Managers in the command line](#special-case-using-one-filtersjson-geofencetxt-alarmsjson-etc-for-all-managers-from-the-command-line)
    * [Using `config.ini` to simplify Manager... management](#using-configini-to-simplify-manager-management)
    * [Naming your Managers](#naming-your-managers)
    * [Running Multiple Instances of the PokeAlarm Server](#running-multiple-instances-of-the-pokealarm-server)
* [Final notes](#final-notes)

## Before you begin

* Deadly has to eat! Get the word out about PokeAlarm and send a [Paypal tip](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5W9ZTLMS5NB28&lc=US&item_name=PokeAlarm&currency_code=USD) or [Patreon pledge](https://www.patreon.com/pokealarm) his way for a job well done and to keep the features coming.
* Version 3.1 is now in the master branch. Read the patch notes if you are upgrading from version 3.
* Version 2 is now in a separate branch, [v2](https://github.com/kvangent/PokeAlarm/tree/v2)
* If you have experience with PokeAlarm v2, use the .example files in v3 root to quickly get started
* Features are constantly being added. Always visit the #announcements discord channel for udpates
* Contact us in the [#troubleshooting discord channel](https://discordapp.com/channels/215181169761714177/218822834225545216) or open a ticket on our [github page](https://github.com/RocketMap/PokeAlarm/issues)

## Notes

* If RocketMap is not configured to send moves or IVs for particular pokemon, e.g., `-eblk`, then you will get a `unkn` message for stats if you do not set that particular pokemon to `"false"` in `filters.json`.  This behavior is intentional in PokeAlarm v3. This is to ensure that you get the snorlax notification even if RocketMap sends the webhook without IVs or moves.  To bypass, use `"ignore_missing":"True"` in your `filters.json` either globally or individually for each Pokemon.
* RocketMap webhooks have been recently undergoing changes.  You may see errors in the PokeAlarm v3 log such as `[    MainProcess][WebhookStr][   ERROR] Encountered error while processing webhook (TypeError: int() argument must be a string or a number, not 'NoneType')
`. This is because RocketMap is sending new webhook information that PokeAlarm hasn't yet incorporated.  Your PokeAlarm setup will still function normally.
* Remember - you only need to edit the JSON, `geofence.txt`, and `config.ini` files.  Other modifications to the code are not supported!!!
* PyCharm is a great IDE to manage your JSON and config files.  The EDU edition is free: https://www.jetbrains.com/pycharm-edu . This will will help you avoid those pesky formatting errors.
* Alternatively, use an online JSON editor like http://www.jsoneditoronline.org which will yell at you if the json is incorrectly formatted

## Introduction
PokeAlarm v3 takes advantage of multiprocessing to simplify running multiple configurations. To further simplify configuration, the `alarms.json` as you know it in v2 has been split into `alarms.json` and `filters.json`.  Geofencing is still handled by `geofence.txt`, which now allows for multiple geofences in the same file.  You can add multiple config files in a list in `config.ini`.

Here's a visual on the PokeAlarm v3 workflow:

![](../images/v3_overview.png)

* The PokeAlarm Server is initiated by `start_pokealarm.py`
* The number of managers is set etiher in the command line or `config.ini`
* Each Manager is assigned a `filters.json`, `geofence.txt` (optional), and `alarms.json`
* `filters.json` contains the pokemon, gym, and pokestop configs
* `geofences.txt` is optional, and contains coordinates for one or more areas to limit notifications
* `alarms.json` contains one or more services, e.g., twitter, slack, discord, to send the custom notifications

## Changes to JSON files

The `alarms.json` in PokeAlarm v2 contained four sections - alarms, gyms, pokemon, pokestops.

In PokeAlarm v3, the configuration has been split between three files - filters, geofences, and alarms:

| config file | description |
|:-----------:|:----------|
`filters.json` | enables pokemon, gym, and pokestop settings
`geofence.txt` | optional, handles geofence(s)
`alarms.json` | configures alarms only

See the .example files in your PokeAlarm root directory for sample setups.

### Config file: `filters.json`

* This is a **required** file
* The `pokemon:` section in the PokeAlarm v2 has been moved to its own file, `filters.json`.

#### Gyms

```
"gyms":{
    "enabled":"False",
    "ignore_neutral":"False",
    "filters":[
        {
            "from_team":["Valor", "Instinct", "Mystic"], "to_team":["Valor", "Instinct", "Mystic"],
            "min_dist":"0", "max_dist":"inf"
        }
    ]
},
```

* A new key, `ignore_neutral`, has been added.  This is to prevent those "It is now controlled by Neutral" gym messages.
* The keys for each team have been simplified. Setting a team value to `True` will filter for any gym action for that particular team.

### Changes in move filtering

#### Filtering on a single `quick_move`
The following example will filter for Dragonites with Dragon Breath.  In Version 3, you must wrap the move in brackets `[ ]`.

`"Dragonite": { "quick_move": [ "Dragon Breath" ] }`

#### Filtering on multiple `charge_move` moves

The following example will filter for Dragonites with either Dragon Claw or Hyper Beam.  In Version 3, you must wrap the moves in brackets `[ ]`, and separate each move with a comma `,`.

`"Dragonite": { "charge_move": [ "Dragon Claw", "Hyper Beam" ] }`

#### NEW: filtering on `moveset`

New to PokeAlarm Version 3 is the ability to filter on a moveset, that is, a specific combination of `quick_move` AND `charge_move`.  This is useful for looking for attacking or defending Pokemon.

The following example will filter for Dewgong with Frost Breath and Blizzard:

`"Dewgong": { "moveset": [ "Frost Breath/Blizzard" ] }`

The following example will filter for Dragonites with either
* Dragon Breath AND Dragon Claw

OR

* Steel Wing AND Dragon Pulse

`"Dragonite": { "moveset": [ "Dragon Breath/Dragon Claw", "Steel Wing/Dragon Pulse" ] }`

### NEW: filtering on `size`

Want those tiny Rattata and big Magikarp badges?  Here's how to add them to your `filters.json`.  (Remember, you'll need two different JSON files if you're looking for either high IV or XL karp.)

```json
"Rattata":{"size":['tiny'] },
"Magikarp":{ "size":['big'] },
```

If you'd like to filter on other sizes, select from the following:

**PokeAlarm Version 3**

| Filter | Description, Version 3 |
|:------:|:------------|
| `size` | `"XS"`,`"Small"`, `"Normal"`, `"Large"`, `"XL"`

**PokeAlarm Version 3.1** renames `XS` and `XL` to `tiny` and `big`, to better match in-game text.

| Filter | Description, Version 3.1 |
|:------:|:------------|
| `size` |`"tiny"`,`"small"`, `"normal"`, `"large"`, `"big"`

#### New: Optional ignoring of pokemon with missing IVs or moves
If RocketMap is not configured to send moves or IVs for particular pokemon, e.g., `-eblk`, then you will get a `unknown` message for notifications if you do not set that particular pokemon to `"false"` in `filters.json`. This behavior is intentional in PokeAlarm v3. This is to ensure that you get the Snorlax notification even if RocketMap sends the webhook without IVs or moves.

To bypass, use `"ignore_missing":"True"` in your `filters.json` either globally or individually for each Pokemon.

`"Pidgey": { "ignore_missing":"True" }`

It is highly recommended to disable this option for the rares - snorax, dragonite, lapras - since you'll want to be notified of those, regardless of stats.

### Config file: `geofence.txt` (optional)

* This is an *optional* file
* In version 3, you are permitted to have multiple geofences in a single file.  In order to distinguish between different geofences, each set of coordinates in your geofence.txt file must contain a header with a set of brackets, like so:

```
[Central Park]
40.801206,-73.958520
40.767827,-73.982835
40.763798,-73.972808
40.797343,-73.948385

[Other Place]
61.801206,-100.958520
61.767827,-100.982835
61.763798,-100.972808
61.797343,-100.948385

```

PokeAlarm v3 will fail otherwise.

### Config file: `alarms.json`
* This is a **required** file
* the `alarms:[]` section in PokeAlarm v2 configuration file has been moved into its own file, `alarms.json`
* The `alarms:` key has been removed from the file. Otherwise, everything is the same from v2
* You may copy your alarm configuration from v2 into v3
* The existing documentation for Alarm services should still be applicable to PokeAlarm v3.  Some keys have changed in v3.1

#### New Filters


#### New and updated Dynamic Text Substitutions
Version 3 adds new DTS options and makes slight changes to some existing ones.

| Version 2 | Version 3  | Version 3.1 | Notes |
|:---------:|:----------:|:------------:|:------|
| | | `<geofence>` | Name of the geofence where the alerted Pokemon originated
| `<id>`    | `<pkmn_id>`| No Change | Pokemon ID. Primarily affects Pokemon image URL in notification
| `<move1>` | `<quick_move>` | `<quick_move>` | Added underscore to match code styling of project
| `<move2>` | `<charge_move>` | `<charge_move>` | Added underscore to match code styling of project
|           | `<min_dist>` | No Change | New option
|           | `<max_iv>` | No Change | | New option. When coupled with `<min_iv>`, useful for filtering on a specific IV range of pokemon.  Or useful for finding 0% IV pokemon? :)
|           | `<iv_0>` | No Change | IV, rounded to 0 decimals (great for Twitter)
|           | `<iv_2>` | No Change | IV, rounded to 2 decimals
| | |`<quick_id>`
| | `<quick_damage>` | `<quick_damage>` |
| | `<quick_dps>` |`<quick_dps>` |
| | `<quick_duration>` | `<quick_duration>`
| | `<quick_energy>` | `<quick_energy>`
| | |`<charge_id>`
| | `<charge_damage>` | `<charge_damage>`
| | `<charge_dps>` | `<charge_dps>`
| | `<charge_duration>` | `<charge_duration>`
| | `<charge_energy>` | `<charge_energy>`
| | `<gender>` | No Change
| | `<weight>` | No Change
| | `<height>`| No Change
| | `<size>` | No Change
Want more options? [Buy Deadly a beer](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5W9ZTLMS5NB28&lc=US&item_name=PokeAlarm&currency_code=USD) and maybe he'll come around. =P

## Upgrading from PokeAlarm Version 2 to Version 3.1

Run the following commands:
```
git pull
pip install -r requirements.txt
```

If you run into significant issues during the pull, back up your JSON and config.ini files, then clone Pokelarm again.

Remember that there are significant changes to the JSON files, so be sure that you've completed the prior steps before running PokeAlarm version 3.


## Running PokeAlarm v3
PokeAlarm v3 is now started by running `start_pokealarm.py`.

### Optional Arguments for `start_pokealarm.py`
Type `start_pokealarm.py -h` to view a list of arguments.  Arguments that start with `--`, e.g., `--key`,  can also be set in `config.ini`, located in the `config` folder of your PokeAlarm root directory.  Command line values will override values stored in `config.ini`.

The list of arguments are below:


| Argument    | Default | Description
|:------------|:-------:|:-----------|
| `-h`, `--help`  | | show this help message and exit
| `-cf`, `--config`| `config/config.ini` | Specify configuration file other than config.ini
| `-d`, `--debug` |  |          Debug Mode
| `-H HOST`, `--host HOST` | `127.0.0.1` | Set web server listening host
| `-P PORT`, `--port PORT` | `4000` |  Set web server listening port
| `-m MANAGER_COUNT`, `--manager_count MANAGER_COUNT` | `1` | Number of Manager processes to start
| `-M MANAGER_NAME`, `--manager_name MANAGER_NAME` | | Names of Manager processes to start
| `-k KEY`, `--key KEY` | | Specify a Google API Key to use.
| `-f FILTERS`, `--filters FILTERS` | `filters.json` | Filters configuration file
| `-a ALARMS`, `--alarms ALARMS` | `alarms.json` | Alarms configuration file
| `-gf GEOFENCES`, `--geofences GEOFENCES` | | file containing list of coordinates to define a geofence
| `-l LOCATION`, `--location LOCATION` | | Location, can be an address or coordinates
| `-L {de,en,es,fr,it,pt,zh_hk}`, `--locale {de,en,es,fr,it,pt,zh_hk}` | |Locale for Pokemon and Move names: default en, check locale folder for more options
| `-u {metric,imperial}`, `--units {metric,imperial}` | | Specify either metric or imperial units to use for distance measurements.
| `-tl TIMELIMIT`, `--timelimit TIMELIMIT` | | Minimum number of seconds remaining on a pokemon to send a notify
| `-tz TIMEZONE`, `--timezone TIMEZONE` | |  Timezone used for notifications. Ex: `America/Los_Angeles`. Visit [this article](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for a list of valid timezones.

Running `start_pokealarm.py` will start the PokeAlarm server and assume the following as default:

```
Host: 127.0.0.1
Port: 4000
filters: filters.json
alarms: alarms.json
```

Which is equivalent to running the command below:

`start_pokealarm.py -H 127.0.0.1 -P 4000 -f filters.json -a alarms.json`

### Running multiple alarms, filters, etc., in a single `start_pokealarm.py` instance from the command line
Version 3 requires `filters.json` and `alarms.json`.  `Geofence.txt` is optional.

| Command line parameter | default | Desciption |
|-----------|:----------:|---------------------|
`-f FILTERS.JSON` | `filters.json` | your desired pokemon, gym, and pokestop filters.  Visit the [Filters](Filters) wiki article for more details.
`-gf GEOFENCE_FILE` | `geofence.txt` | File containing a list of coordinates for one or more geofence. Requires a header, in brackets `[ ]`, before each list of coordinates.  Visit the [Geofences](geofences) wiki article for more details.
`-a ALARMS.JSON` | `alarms.json` | set of alarms, or services, e.g., Twitter, Discord, Slack.  Visit the [Alarms](alarms) wiki article for details.
`-m NUMBER_OF_MANAGERS` | `1` | number of total PokeAlarm Managers (processes)

### Running one Manager from the command line
If you want just one manager with one geofence, filter, and alarm config, run like so:

`start_pokealarm.py -m 1 -f filters.json -gf geofences.txt -a alarms.json`

(`-m 1` is the default.  It's added above just for clarity. You can skip if you plan on running only 1 Manager.)

### Running two Managers from the command line
If you want to run 2 managers, each with it's own filters, geofence, and alarms, you need to specify them in the desired order like so:

`start_pokealarm.py -m 2 -f filters1.json -gf geofences1.txt -a alarms1.json -f filters2.json -gf geofences2.txt -a alarms2.json`

This way, the configs are matched like so:

| Manager Number | filter | geofence | alarm |
|:--------------:|:------:|:--------:|:-----:|
| Manager 1 | `filters1.json`| `geofences1.txt` | `alarms1.json` |
| Manager 2 | `filters2.json`|`geofences2.txt` | `alarms2.json` |

### Special case: using one `filters.json`, `geofence.txt`, `alarms.json`, etc., for all Managers from the command line
Let's say you want one `filters_all.json` for two managers, like so:

| Manager | Description |
|:-------:|:-----------:|
| PokeAlarm Manager 1 | `filters_all.json`, `geofences1.txt`, and `alarms1.json`
| PokeAlarm Manager 2 | `filters_all.json`, `geofences2.txt`, and `alarms2.json`

If you run `start_pokealarm.py` with more than one manager and only specify one `-f filters_all.json` in the command line, PokeAlarm v3 will assign that `filters_all.json` to all managers.  For example:

`start_pokealarm.py -m 2 -f filters_all.json -gf geofences1.txt -a alarms1.json -gf geofences2.txt -a alarms2.json`

### Using `config.ini` to simplify Manager... management
To faciliate multiple combinations of managers, filters, alarms, geofences, etc., PokeAlarm v3 allows you add a list of these parameters in `config.ini`.

Scenario:  Let's say you want to run PokeAlarm for 2 areas - Los Angeles and Tokyo - with 2 filters each (`filters_main.json`, `filters_nearby.json`).  Three geofences are desired (`geofence_la.txt`, `None`, and `geofence_tk.txt`), and one alarm config each (`alarms_la_v3.json` and `alarms_tk_v3.json`) is added, for a total of 4 PokeAlarm managers.

In a table, it looks like this:

| Manager Number | Parameter | Value |
|:--------------:|:---------:|:-----:|
| 1 | location | `"Los Angeles CA"` |
| 1 | filter | `filters_main.json`|
| 1 | geofence | `geofence_la.txt` |
| 1 | alarms | `alarms_la.json` |
| 1 | unit | `imperial` |
| 1 | timezone | `Amer\Los_Angeles` |
| --------|---------- |-------|
| 2 | location | `"Los Angeles CA"` |
| 2 | filter | `filters_nearby.json`|
| 2 | geofence | `None` |
| 2 | alarms | `alarms_la.json` |
| 2 | unit | `imperial` |
| 2 | timezone | `Amer\Los_Angeles` |
| --------|---------- |-------|
| 3 | location | `"Tokyo Japan"` |
| 3 | filter | `filters_main.json`|
| 3 | geofence | `geofence_tk.txt` |
| 3 | alarms | `alarms_tk.json` |
| 3 | unit | `metric` |
| 3 | timezone | `Amer\Los_Angeles` |
| --------|---------- |-------|
| 4 | location | `"Tokyo Japan"` |
| 4 | filter | `filters_nearby.json`|
| 4 | geofence | `None` |
| 4 | alarms | `alarms_tk.json` |
| 4 | unit | `metric` |
| 4 | timezone | `Amer\Los_Angeles` |

In the CLI, it would look like this:

`start_pokealarm.py -l "Los Angeles CA" -l "Los Angeles CA" -l "Tokyo Japan" -l "Tokyo Japan" -f filters_main.json -f filters_nearby.json -f filters_main.json -f filters_nearby.json -gf geofence_la.txt -gf None -gf geofence_tk.txt -gf geofence_tk.txt -a alarms_la_v3.json -a alarms_la_v3.json -a alarms_tk_v3.json -a alarms_tk_v3.json -u imperial -u imperial -u metric -u metric -tz America/Los_Angeles`

Pretty beastly, right? Here's an example of how to configure `config.ini` to achieve the same goal:

```
manager_count: 4
location: [ "Los Angeles CA",  "Los Angeles CA",    "Tokyo Japan",     "Tokyo Japan"       ]
filter:   [ filters_main.json, filters_nearby.json, filters_main.json, filters_nearby.json ]
geofence: [ geofence_la.txt,   None,                geofence_tk.txt,   geofence_tk.txt     ]
alarms:   [ alarms_la_v3.json, alarms_la_v3.json,   alarms_tk_v3.json, alarms_tk_v3.json   ]
unit:     [ imperial,          imperial,            metric,            metric              ]
timezone: America/Los_Angeles

```
(The spacing for alignment is purely for aesthetic purposes.)

You would then run the following to launch the PokeAlarm server:

`start_pokealarm.py`

That's it. (=0

Some notes:

* Order is important - the list elements are index matched with each other
* The geofence line in the example above contains a `None` entry, meaning that the second Manager will not use a geofence
* Location syntax is finicky. Use `"Los Angeles CA"` but not `"Los Angeles, CA"`.  The comma will mess things up
* The `timezone` with only one element, `America/Los_Angeles`, will apply to all 4 managers.  Don't wrap the timezone in double quotes

The following parameters can be set in a list in `config.ini`:
* key
* manager name
* location
* filters
* geofences
* alarms
* unit
* timelimit

### Naming your Managers
Similar to `-sn` in RocketMap, you can name individual PokeAlarm Managers.  This helps to make the log files easier to read.   

* Use `-M "Manager 1" -M "Manager 2" -M "Manager 3"` in the commandline
* In `config.ini`, use `manager_name: [ "Manager 1, "Manager 2", "Manager 3" ]` in a list.
    * Tip: As I did above, you can add extra white spaces to line up the different managers in `config.ini` for aesthetics

### Running Multiple Instances of the PokeAlarm Server
Use the `-cf` flag for each instance you plan to run.  Make sure that each instance is using a different port.
```
start_pokealarm.py -cf config1.ini
start pokealarm.py -cf config2.ini
```

## Final notes

* The wiki is being overhauled to reflect the above notes and more.
* If you have questions that haven't been addressed in this quick start guide, hit us up in the discord channel or submit a ticket on the Github page.
*  If you enjoy PokeAlarm, [please support the developer by sending a small donation.](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5W9ZTLMS5NB28&lc=US&item_name=PokeAlarm&currency_code=USD) PokeAlarm is used by literally thousands of people on a daily basis. Pretty much every public twitter feed uses PokeAlarm - why not send a beer to the dev for a job well done? (=0 Happy Hunting and Good Luck!
