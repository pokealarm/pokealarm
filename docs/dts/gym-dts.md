# Gym DTS

## Overview

* [Prerequisites](#prerequisites)
* [Available DTS](#available-dts)

## Prerequisites

This page assumes:

1. You have a working scanner.
2. You read and understood the [DTS](dynamic-text-substitution) page.
3. You are using the latest version of PokeAlarm.

## Available DTS

| DTS             | Description                                              |
|---------------- |--------------------------------------------------------- |
| gym_id          | The gym id. Unique per gym.                              |
| lat             | Latitude of the gym.                                     |
| lng             | Longitude of the gym.                                    |
| lat_5           | Latitude of the gym, truncated to 5 decimal places.      |
| lng_5           | Longitude of the gym, truncated to 5 decimal places.     |
| distance        | Distance of the gym from the set location.               |
| direction       | Cardinal direction of the gym, from the set location.    |
| gmaps           | Google Maps link to the location of the gym.             |
| applemaps       | Apple Maps link to the location of the gym.              |
| geofence        | Geofence around the event. See 'Geofences' section from [filters](filters-overview#geofence) page.|
| old_team        | The team in control of the gym previously.               |
| old_team_id     | The id of the team in control of the gym previously.     |
| old_team_leader | The leader of the team in control of the gym previously. |
| new_team        | The team currently in control of the gym.                |
| new_team_id     | The id of the team currently in control of the gym.      |
| new_team_leader | The leader of the team currently in control of the gym.  |
| gym_name        | * The name of the gym.                                   |
| gym_description | * The description of the gym.                            |
| gym_image       | * The url to the image of the gym.                       |
| slots_available | Number of open guard slots available in a gym.           |
| guard_count     | number of guards assigned to a gym.                      |

\* Gym Info require caching. See the
[Object Caching](object-caching) page for more information.
