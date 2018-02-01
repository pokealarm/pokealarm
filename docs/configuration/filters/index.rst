Filters
========

## Overview

* [Prerequisites](#prerequisites)
* [Introduction](#introduction)
* [Filter Parameters](#filter-parameters)
* [Defaults](#defaults)
* [Advanced](#advanced)
  * [Missing Info](#missing-info)
  * [Geofence](#geofence)
  * [Custom DTS](#custom-dts)

## Prerequisites
This guide assumes:

1. You have a working scanner
2. You are familiar with
[JSON formatting](https://www.w3schools.com/js/js_json_intro.asp)
3. You are using the latest version of PokeAlarm

## Introduction

**Filters** are used to determine which Events trigger notifications.
When PA receives information about an event, it is compared to the
filters defined in your `filters.json` configuration file.

A `filters.json` file is composed of a single JSON object with five
different subsections. Each section defines different settings for each
different type of event. A list of parameters available for each type of
filter can be found on the following pages:
* [Monsters](Monster-Filters)
* [Stops](Stop-Filters)
* [Gyms](Gym-Filters)
* [Eggs](Egg-Filters)
* [Raids](Raid-Filters)

The basic structure of `filters.json` is as follows:

```json
{
    "monsters":{
        "enabled": false,
        "defaults": { },
        "filters": { }
    },
    "stops":{
        "enabled": false,
        "defaults": { },
        "filters": { }
    },
    "gyms":{
        "enabled": false,
        "ignore_neutral": false,
        "defaults": { },
        "filters": { }
    },
    "eggs":{
        "enabled": false,
        "defaults": { },
        "filters": { }
    },
    "raids":{
        "enabled": false,
        "defaults": { },
        "filters": { "filter-name" : { } }
    }
}
```

## Filter Parameters

Each section contains a `"filters"` subsection as a json object with
filters represented as key-value pairs. The key represents the
**filter name** paired to the corresponding **filter parameters**. Each
type of Event contains it's own parameters, which are listed on the
corresponding filters page for each filter.

**IMPORTANT:** Filter's ONLY check parameters IF you list them.
Don't enter parameters that you don't want - this can cause unwanted
affects (for example `"min_dist"` with `"is_missing_info":true` will
reject ALL events if the server setting `location` is not set)

An example filters section looks like this:

```json
"filters": {
    "filter_name_1": {
        "monsters": [ 1, 2, 3 ],
        "min_iv": 90.0, "max_iv": 100
    },
    "filter_name_2": {
        "monsters": [ 4, 5, 6 ],
        "min_iv": 90.0, "max_iv": 100
    }
}
```

The details of an event are only checked if it is defined as a filter
parameter. For example, a monster's species will only be checked by a
filter if the filter has the `"monsters"` parameter defined.

Currently, a notification will only be triggered by the first filter it
passes - additional filters will NOT be checked once a match it found.

## Defaults

You can use the `"defaults"` section to easily apply default values to
all of the filters in that section.

For example, the following section:

```json
"defaults": { "min_iv": 90.0, "max_iv": 100 },
"filters": {
    "filter_name_1": { "monsters": [ 1, 2, 3 ] },
    "filter_name_2": { "monsters": [ 4, 5, 6 ] }
}
```

Which is equivalent to:

```json
"filters": {
    "filter_name_1": {
        "monsters": [ 1, 2, 3 ],
        "min_iv": 90.0, "max_iv": 100
    },
    "filter_name_2": {
        "monsters": [ 4, 5, 6 ],
        "min_iv": 90.0, "max_iv": 100
    }
}
```

Additionally, you can override or even disable defaults. Override them
by adding a new value, or disable them by using `null`. An example of
this is:

```json
"defaults": { "min_iv": 90.0, "max_iv": 100 },
"filters": {
    "filter_name_1": {
        "monsters": [ 1, 2, 3 ],
        "min_iv": 85
    },
    "filter_name_2": {
        "monsters": [ 4, 5, 6 ],
        "min_iv": null, "max_iv": null
    }
}
```

Which is equivalent to:

```json
"filters": {
    "filter_name_1": {
        "monsters": [ 1, 2, 3 ],
        "min_iv": 85, "max_iv": 100
    },
    "filter_name_2": { "monsters": [ 4, 5, 6 ] }
}
```

If a parameter is set to `null`, it is the same as not being set all.

## Advanced

### Missing Info

For a variety of reasons, an Event may be missing information needed to
properly check it. In these cases, the `"is_missing_info"` parameter
decides how a filter handles it.

**IMPORTANT:** `"is_missing_info"`: ONLY applies to necessary
information. Information is necessary only if being used to filter. If
`"min_iv"` or `"max_iv"` aren't set, it doesn't matter if `iv` is
unknown or not.

With the `"is_missing_info": false` parameter, filters will ONLY allow
Events with all necessary information. If `"min_dist"` is set but the
`dist` is unknown, it will be rejected.

With the `"is_missing_info": true` parameter, filters will ONLY allow
Events that ARE MISSING INFOrmation. If `"max_iv"` is set and the ivs
are unknown, it will be rejected.

When `"is_missing_info"` is NOT included in the filter, it will simply
skip any checks on missing information. If you have `"min_iv":90.0` set
but no `"is_missing_info`", PA will still pass monsters
where `iv` is unknown.

### Geofence

For more information on configuring your `geofence.txt`, see the
[Geofence](geofences) page.

You can require an Event to be inside specific geofences for a Filter.

This example will check if an event is inside either `"fence1"` or
`"fence2"` as defined in:

```json
"filter_name_1": {
    "geofences": [ "fence1", "fence2" ]
}
```

Geofences are checked in order. The first geofence with the event inside
 will be used to define the `<geofence>` DTS.

If no geofences are set, the `<geofence>` DTS will always return
`unknown`.

If a geofence with the set name does not exist, it will be skipped and
an error will print out to the console.

Another example would be to configure alerts inside all of your geofences.
You just have to configure the geofences like this:

```json
"filter_name_1": {
    "geofences": [ "all" ]
}
```

### Custom DTS

**Note:** See the [Dynamic Text Substitution](Dynamic-Text-Substitution)
page for an explanation on using DTS.

Custom DTS are filter specific DTS options that are added to the DTS for
an Event when it passes a filter. The `"custom_dts"` parameter can
contain key-value pairs of DTS that ONLY apply for that filter.

For example:

```json
"filters": {
    "filter_name_1": {
        "monsters": [ 1, 2, 3 ],
        "custom_dts": { "family": "Grass starters" }
    },
    "filter_name_2": {
        "monsters": [ 4, 5, 6 ],
        "custom_dts": { "family": "Fire starters" }
    }
}
```

If the event passes the first filter, the text `<family>` will return
`Grass starters`. if it passes the second filter, the text will return
`Fire Starters`.

Custom DTS can be used for a variety of different things, including
customizing the Discord Webhook or Slack Channel. However they can never
override original DTS's.

Currently, Custom DTS cannot make use of regular DTS.


.. toctree::
   :glob:

   *