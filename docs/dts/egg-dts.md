# Egg DTS

## Overview

* [Prerequisites](#prerequisites)
* [Available DTS](#available-dts)

## Prerequisites

This page assumes:

1. You have a working scanner.
2. You read and understood the [DTS](dynamic-text-substitution) page.
3. You are using the latest version of PokeAlarm.

## Available DTS

| DTS             | Description                                             |
|---------------- |-------------------------------------------------------- |
| gym_id          | The gym id. Unique per gym.                             |
| egg_lvl         | The tier level of the egg.                              |
| hatch_time_left | Time remaining until the egg hatches.                   |
| 12h_hatch_time  | Time when the egg will hatch, formatted in 12h.         |
| 24h_hatch_time  | Time when the egg will hatch, formatted in 24h.         |
| raid_time_left  | Time remaining until the raid ends.                     |
| 12h_raid_end    | Time when the raid ends, formatted in 12h.              |
| 24h_raid_end    | Time when the raid ends, formatted in 24h.              |
| lat             | Latitude of the raid.                                   |
| lng             | Longitude of the raid.                                  |
| lat_5           | Latitude of the raid, truncated to 5 decimal places.    |
| lng_5           | Longitude of the raid, truncated to 5 decimal places.   |
| distance        | Distance of the raid from the set location.             |
| direction       | Cardinal direction of the raid, from the set location.  |
| gmaps           | Google Maps link to the location of the raid.           |
| applemaps       | Apple Maps link to the location of the raid.            |
| geofence        | Geofence around the event. See 'Geofences' section from [filters](filters-overview#geofence) page.|
| gym_name        | * The name of the gym.                                  |
| gym_description | * The description of the gym.                           |
| gym_image       | * The url to the image of the gym.                      |
| team_id         | The id of the team currently in control of the gym.     |
| team_name       | The team currently in control of the gym.               |
| team_leader     | The leader of the team currently in control of the gym. |

\* Gym Info requires caching. See the
[Object Caching](object-caching) page for more information.
