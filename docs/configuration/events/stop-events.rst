Stops
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

A **Stop Event** represents when a stop is lured.


Available DTS
-------------------------------------


General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

============== ==============================
DTS            Description
============== ==============================
stop_id        The stop id. Unique per stop.
stop_name      The name of the stop.
stop_image     URL to the image of the stop.
lure_type_id   The id of the active lure.
lure_type_name The name of the active lure.
============== ==============================


Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Geofences are only evaluated per Filter - ``<geofence>`` will be unknown if
    it passes through a Filter without a ``geofences`` restriction applied.

============ ======================================================
DTS          Description
============ ======================================================
lat          Latitude of the stop.
lng          Longitude of the stop.
lat_5        Latitude of the stop, truncated to 5 decimal places.
lng_5        Longitude of the stop, truncated to 5 decimal places.
distance     Distance of the stop from the set location.
direction    Cardinal direction of the stop, from the set location.
gmaps        Google Maps link to the location of the stop.
applemaps    Apple Maps link to the location of the stop.
waze         Waze link to the location of the stop.
geofence     Geofence around the event.
============ ======================================================


Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

===================== =================================================================== ===========
DTS                   Description                                                         Example
===================== =================================================================== ===========
time_left             Time remaining until the lure expires.                              1h 15m 52s
12h_time              Time that the lure will disappear, in a 12h format.                 01:15:52pm
24h_time              Time that the lure will disappear, in a 24h format.                 13:15:52
time_left_no_secs     Time remaining until the lure expires without seconds.              1h 15m
12h_time_no_secs      Time that the lure will disappear, in a 12h format without seconds. 01:15pm
24h_time_no_secs      Time that the lure will disappear, in a 24h format without seconds. 13:15
time_left_raw_hours   Hours only until the lure expires.                                  1
time_left_raw_minutes Minutes only until the lure expires.                                15
time_left_raw_seconds Seconds only until the lure expires.                                52
===================== =================================================================== ===========
