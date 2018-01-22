# Egg Filters

## Overview

* [Prerequisites](#prerequisites)
* [Introduction](#introduction)
* [Parameters](#parameters)

## Prerequisites

This page assumes:

1. You have a working scanner.
2. You are familiar with
[JSON formatting](https://www.w3schools.com/js/js_json_intro.asp).
3. You are using the latest version of PokeAlarm.
4. You have read and understood the [Filters Overview](filters-overview)
page.

## Introduction

The `"eggs"` section has three distinct settings.

| Setting Name         | Description                                               |
| -------------------- |---------------------------------------------------------- |
| enabled              | Process Egg Events only if `true`                         |
| defaults             | See [filters](filters-overview#defaults) page on defaults |
| filters              | See below parameters                                      |

## Parameters

Egg Filters can use the following parameters to filter Egg Events:

| Parameter     | Description                                   | Example |
| ------------- |---------------------------------------------- |---------|
| min_dist      | Min distance of event from set location in miles or meters (depending on settings). | `0.0` *|
| max_dist      | Max distance of event from set location in miles or meters (depending on settings). | `1000.0` *|
| min_time_left | Minimum time (in seconds) until egg hatches.  | `1000`  |
| max_time_left | Maximum time (in seconds) until egg hatches.  | `2400`  |
| min_egg_lvl   | Minimum level of the egg when hatched.        | `0`     |
| max_egg_lvl   | Maximum level of the egg when hatched.        | `5`     |
| current_teams | List of allowed current teams, by id or name. | `[ "Instinct", "Mystic" ]` |
| gym_name_contains | List of regex's required to be in the gym name.  | `[ "Sponsored" , "West\\sOak"]` |
| geofences     | See [filters](filters-overview#geofence) page on 'Geofences'    | `[ "geofence1", "geofence2" ]` |
| custom_dts    | See [filters](filters-overview#custom-dts) page on 'Custom DTS'   | `{ "dts1" : "substitution" }` |
| is_missing_info | See [filters](filters-overview#missing-info) page on 'Missing Info' | `true` or `false` |

\* Floats can use `"inf"` to represent infinity
