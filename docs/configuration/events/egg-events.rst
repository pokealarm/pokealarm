Eggs
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:


Prerequisites
-------------------------------------

This pages assumes the following:

1. You have a working scanner.
2. You read and understood the :ref:`events_dts` page.
3. You are using the latest version of PokeAlarm.

Description
-------------------------------------

A **Egg Event** represents when a egg event appears in a gym.


Available DTS
-------------------------------------

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= ========================================================
DTS               Description
================= ========================================================
gym_id            The gym id. Unique per gym.
egg_lvl           The tier level of the egg.
gym_name          The name of the gym. *
gym_description   The description of the gym. *
gym_image         The url to the image of the gym. *
ex_eligible       True if the gym currently has an ex tag, False if not.
is_exclusive      True if the egg is for an ex raid, False if not.
park              The name of the park the gym is located in.
team_id           The id of the team currently in control of the gym.
team_name         The team currently in control of the gym.
team_leader       The leader of the team currently in control of the gym.
sponsor_id        The sponsor if of the gym. 0 if not sponsored.
sponsored         True if sponsored, False if not.
================= ========================================================

.. note::

  \* Gym Info requires caching. See the :ref:`object-caching`
  page for more information.


Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Geofences are only evaluated per Filter - ``<geofence>`` will be unknown if
    it passes through a Filter without a ``geofences`` restriction applied.

=================== =========================================================
DTS                 Description
=================== =========================================================
lat                 Latitude of the egg.
lng                 Longitude of the egg.
lat_5               Latitude of the egg, truncated to 5 decimal places.
lng_5               Longitude of the egg, truncated to 5 decimal places.
distance            Distance of the egg from the set location.
direction           Cardinal direction of the egg, from the set location.
gmaps               Google Maps link to the location of the egg.
applemaps           Apple Maps link to the location of the egg.
waze                Waze link to the location of the egg.
geofence            Geofence around the event.
=================== =========================================================


Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

======================= =============================================================== =============
DTS                     Description                                                     Example
======================= =============================================================== =============
hatch_time_left         Time remaining until the egg hatches.                           1h 52m 15s
12h_hatch_time          Time when the egg will hatch, formatted in 12h.                 01:15:15pm
24h_hatch_time          Time when the egg will hatch, formatted in 24h.                 13:15:15
hatch_time_no_secs      Time remaining until the egg hatches without seconds.           1h 52m
12_hatch_time_no_secs   Time when the egg will hatch, formatted in 12h without seconds. 01:15pm
24h_hatch_time_no_secs  Time when the egg will hatch, formatted in 24h without seconds. 13:15
hatch_time_raw_hours    Hours only until the egg will hatch.                            1
hatch_time_raw_minutes  Minutes only until the egg will hatch.                          52
hatch_time_raw_seconds  Seconds only until the egg will hatch.                          29
raid_time_left          Time remaining until the raid ends.                             1h 52m 12s
12h_raid_end            Time when the raid ends, formatted in 12h.                      01:15:15pm
24h_raid_end            Time when the raid ends, formatted in 24h.                      13:15:15
raid_time_no_secs       Time remaining until the raid ends without seconds.             1h 52m
12h_raid_end_no_secs    Time when the raid ends, formatted in 12h without seconds.      01:15pm
24h_raid_end_no_secs    Time when the raid ends, formatted in 24h without seconds.      13:15
raid_time_raw_hours     Hours only until the raid will end.                             1
raid_time_raw_minutes   Minutes only until the raid will end.                           52
raid_time_raw_seconds   Seconds only until the raid will end.                           29
======================= =============================================================== =============


Weather
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= =========================================================
DTS               Description
================= =========================================================
weather_id        Weather ID of the egg.
weather           Weather name of the egg.
weather_or_empty  Weather name of the egg, or empty string if unknown.
weather_emoji     Weather emoji of the egg, or empty string if unknown.
================= =========================================================
