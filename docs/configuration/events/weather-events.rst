Weather
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

A **Weather Event** represents a change in the weather for a specific s2 cell.


Available DTS
-------------------------------------


General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= ===========================================================================
DTS               Description
================= ===========================================================================
s2_cell_id        The id of the s2 cell. Unique per cell.
weather_id        The id of the changed weather condition.
weather_emoji     The emoji representing the changed weather condition.
severity_id       The id that represents the severity of the weather. (Either ``0``, ``1``,
                  or ``3``
severity          The severity of the weather. (Example: ``Extreme``)
severity_or_empty The severity of the weather or nothing when there isn't and severe weather.
day_or_night_id   The id representing if it's day or night
day_or_night      The current day type (Either ``Day`` or ``Night``)
================= ===========================================================================


Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Geofences are only evaluated per Filter - ``<geofence>`` will be unknown if
    it passes through a Filter without a ``geofences`` restriction applied.

============ =======================================================================
DTS          Description
============ =======================================================================
lat          Latitude of the center of the s2 cell.
lng          Longitude of the center of the s2 cell.
lat_5        Latitude of the center of the s2 cell, truncated to 5 decimal places.
lng_5        Longitude of the center of the s2 cell, truncated to 5 decimal places.
distance     Distance to the center of the s2 cell from the set location.
direction    Cardinal direction of the center of the s2 cell from the set location.
gmaps        Google Maps link to the center of the s2 cell.
applemaps    Apple Maps link to the center of the s2 cell.
waze         Waze link to the center of the s2 cell.
geofence     Geofence around the event.
============ =======================================================================
