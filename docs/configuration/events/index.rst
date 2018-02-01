Events
=======

## Overview
* [Prerequisites](#prerequisites)
* [Introduction](#introduction)
* [Available DTS](#available-dts)
* [Advanced](#advanced)
  * [Reverse Geocoding](#reverse-geocoding)
  * [Distance Matrix](#distance-matrix)


## Prerequisites
This guide assumes:

1. You have a working scanner.
3. You have read and understood the [Alarms](alarms) page.
4. You are comfortable with the layout of `alarms.json`.
5. You are using the latest version of PokeAlarm.

## Introduction

Dynamic Text Substitutions (or DTS) are special text values that
that are automatically change to useful text. These text values, when
surrounded with diamond brackets (`<` and `>`) are replaced by a value
customized to fit the Event. For example, the following text:

`A wild <mon_name> has appeared! It has <iv>% IVs!`

Will appear as the following if a perfect Charmander is sent:

> A wild Charmander has appeared! It has 100.0% IVs!

Or, it could appear like this if a mediocre Pidgey is sent:

> A wild Pidgey has appeared! It has 55.6% IVs!

If an Event doesn't have the correct information, it may display either
`?`, `???`, or `unknown` as the substitution.

**Warning:** ONLY use the `alarms.json` to customize your notifications.
Editing other files may not work as correctly!

## Available DTS

The DTS that are available depend on the type of Event that trigger's a
notification. Currently PA supports five types of Events:
[Monsters](Monster-DTS), [Stops](Stop-DTS), [Gyms](Gym-DTS),
[Eggs](Egg-DTS), and [Raids](Raid-DTS).

## Advanced

### Reverse Geocoding

**Reverse Geocoding** is a process that to get the name or data of
places where the Events take place. This can be used to get things such
as address, city, state, or more. For more information, see the
Geocoding section of the [Google Maps API](Google-Maps-API-Key) page.

PA will only use Reverse Geocoding for Events that have been triggered.
Each Event will use up a single point of your API quota, regardless
of number of fields or alarms used.

| Text             | Description                                       |
|:---------------- |:--------------------------------------------------|
| `<street_num>`   | Street number of the alert location               |
| `<street>`       | Street name of the alert location                 |
| `<address>`      | Address of the alert location, includes both street number and street name, in that order only |
| `<address_eu>`   | Address of the alert location, in european format (street name and street number) |
| `<postal>`       | Postal code of the alert location                 |
| `<neighborhood>` | Neighborhood code of the alert location           |
| `<sublocality>`  | Sublocality code of the alert location            |
| `<city>`         | City code of the alert location                   |
| `<county>`       | County code of the alert location                 |
| `<state>`        | State code of the alert location                  |
| `<country>`      | Country code of the alert location                |

### Distance Matrix

**Distance Matrix** calculations determine how far away an Event is, for
both time and distance. This can be Walking, Biking, or Driving. These
calculations require a set location, and a Google Maps API key. For more
information, see the Distance Matrix section of the
[Google Maps API](Google-Maps-API-Key) page.

| Text             | Description                                       |
|:---------------- |:--------------------------------------------------|
| `<walk_dist>`    | Estimated walking distance to the alert location  |
| `<walk_time>`    | Estimated walking time to alert location          |

| Text             | Description                                       |
|:---------------- |:--------------------------------------------------|
| `<bike_dist>`    | Estimated bike distance to the alert location     |
| `<bike_time>`    | Estimated bike time to alert location             |


| Text             | Description                                       |
|:---------------- |:--------------------------------------------------|
| `<drive_dist>`   | Estimated drive distance to the alert location    |
| `<drive_time>`   | Estimated drive time to alert location            |

Each table represents 1 API quota used for all parameters per pokemon,
pokestop, or gym regardless of number of fields or alarms specified. For
example, `<walk_time>` and `<drive_time>` would require 2 points, but
`<walk_time>` and `<walk_dist>` would only require 1 (per alert).


.. toctree::
   :glob:

   *