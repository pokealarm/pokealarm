# Stops

## Overview

* [Prerequisites](#prerequisites)
* [Available DTS](#available-dts)

## Prerequisites

This page assumes:

1. You have a working scanner.
2. You read and understood the [DTS](Dynamic-Text-Substitution) page.
3. You are using the latest version of PokeAlarm.

## Available DTS

| DTS          | Description                                            |
|------------- |------------------------------------------------------- |
| stop_id      | The stop id. Unique per stop.                          |
| time_left    | Time remaining until the lure expires.                 |
| 12h_time     | Time that the lure will disappear, in a 12h format.    |
| 24h_time     | Time that the lure will disappear, in a 24h format.    |
| lat          | Latitude of the stop.                                  |
| lng          | Longitude of the stop.                                 |
| lat_5        | Latitude of the stop, truncated to 5 decimal places.   |
| lng_5        | Longitude of the stop, truncated to 5 decimal places.  |
| distance     | Distance of the stop from the set location.            |
| direction    | Cardinal direction of the stop, from the set location. |
| gmaps        | Google Maps link to the location of the stop.          |
| applemaps    | Apple Maps link to the location of the stop.           |
| geofence     | Geofence around the event. See 'Geofences' section from [filters](Filters-Overview#geofence) page.|
