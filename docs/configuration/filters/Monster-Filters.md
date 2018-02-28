# Monsters

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
4. You have read and understood the [Filters Overview](Filters-Overview) page.

## Introduction

The `"monsters"` section has three distinct settings.

| Setting Name         | Description                                               |
| -------------------- |---------------------------------------------------------- |
| enabled              | Process Monster Events only if `true`                     |
| defaults             | See [filters](Filters-Overview#defaults) page on defaults |
| filters              | See below parameters                                      |

## Parameters

Monster Filters can use the following parameters to filter Events:

| Parameter     | Description                                       | Example   |
| ------------- |-------------------------------------------------- |---------- |
| monsters      | Array of allowed monsters, by id or name.         | `[ "Bulbasaur", "2", 3 ]`|
| ignore_monsters | Array of ignored monsters, by id or name.       | `[ "Pidgey", "13", 14 ]`|
| min_dist      | Min distance of event from set location in miles or meters (depending on settings). | `0.0` *|
| max_dist      | Max distance of event from set location in miles or meters (depending on settings). | `1000.0` *|
| min_time_left | Minimum time (in seconds) until monster despawns. | `1000`    |
| max_time_left | Maximum time (in seconds) until monster despawns. | `2400`    |
| min_lvl       | Minimum level of the monster.                     | `0`       |
| max_lvl       | Maximum level of the monster.                     | `40`      |
| min_atk       | Minimum attack IV of the monster.                 | `0`       |
| max_atk       | Maximum attack IV of the monster.                 | `15`      |
| min_def       | Minimum defense IV of the monster.                | `0`       |
| max_def       | Maximum defense IV of the monster.                | `15`      |
| min_sta       | Minimum stamina IV of the monster.                | `0`       |
| max_sta       | Maximum stamina IV of the monster.                | `15`      |
| min_iv        | Minimum total IV percentage of the monster.       | `0.0` *   |
| max_iv        | Maximum total IV percentage of the monster.       | `100.0` * |
| min_cp        | Minimum CP of the monster.                        | `0`       |
| max_cp        | Maximum CP of the monster.                        | `10000`   |
| form_ids      | Array of allowed form ids for a monster.          | `[ 0, "1" ]` |
| quick_moves   | Accepted quick moves, by id or name.              | `[ "Vine Whip", "Tackle"]` |
| charge_moves  | Accepted charge moves, by id or name.             | `[ "Sludge Bomb", "Seed Bomb"]` |
| genders       | Array of acceptable genders. Options: `"male", "female", "neutral"` | `[ "female" ]` |
| min_height    | Minimum height of the monster.                    | `0.0` *   |
| max_height    | Maximum height of the monster.                    | `250.0` * |
| min_weight    | Minimum weight of the monster.                    | `0.0` *   |
| max_weight    | Maximum weight of the monster.                    | `250.0` * |
| sizes         | Array of acceptable sizes. Options: `"tiny", "small", "normal", "large", "big"` | `[ "tiny", "big" ]` |
| weather       | Accepted weathers, by id or name.            | `[ "Clear", 2 ]` |
| geofences     | See [filters](Filters-Overview#geofence) page on 'Geofences'    | `[ "geofence1", "geofence2" ]` |
| custom_dts    | See [filters](Filters-Overview#custom-dts) page on 'Custom DTS'   | `{ "dts1" : "substitution" }` |
| is_missing_info | See [filters](Filters-Overview#missing-info) page on 'Missing Info' | `true` or `false` |

\* Floats can use `"inf"` to represent infinity
