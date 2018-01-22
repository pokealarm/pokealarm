# Stop Filters

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

The `"stops"` section has three distinct settings.

| Setting Name         | Description                                               |
| -------------------- |---------------------------------------------------------- |
| enabled              | Process Stop Events only if `true`                        |
| defaults             | See [filters](filters-overview#defaults) page on defaults |
| filters              | See below parameters                                      |

## Parameters

Stop Filters can use the following parameters to filter Stop Events:

| Parameter     | Description                                  | Example |
| ------------- |--------------------------------------------- |---------|
| min_dist      | Min distance of event from set location in miles or meters (depending on settings). | `0.0` *|
| max_dist      | Max distance of event from set location in miles or meters (depending on settings). | `1000.0` *|
| min_time_left | Minimum time (in seconds) until lure ends.   | `1000`  |
| max_time_left | Maximum time (in seconds) until lure ends.   | `2400`  |
| geofences     | See [filters](filters-overview#geofence) page on 'Geofences'    | `[ "geofence1", "geofence2" ]` |
| custom_dts    | See [filters](filters-overview#custom-dts) page on 'Custom DTS'   | `{ "dts1" : "substitution" }` |
| is_missing_info | See [filters](filters-overview#missing-info) page on 'Missing Info' | `true` or `false` |

\* Floats can use `"inf"` to represent infinity
