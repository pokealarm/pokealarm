Gyms
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

A **Gym Event** represents when a gym has been taken for another team.


Available DTS
-------------------------------------


General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================ ========================================================
DTS              Description
================ ========================================================
gym_id           The gym id. Unique per gym.
old_team         The team in control of the gym previously.
old_team_id      The id of the team in control of the gym previously.
old_team_leader  The leader of the team in control of the gym previously.
new_team         The team currently in control of the gym.
new_team_id      The id of the team currently in control of the gym.
new_team_leader  The leader of the team currently in control of the gym.
gym_name         The name of the gym. *
gym_description  The description of the gym. *
gym_image        The url to the image of the gym. *
slots_available  Number of open guard slots available in a gym.
guard_count      Number of guards assigned to a gym.
sponsor_id        The sponsor if of the gym. 0 if not sponsored.
sponsored         True if sponsored, False if not.
================ ========================================================

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
lat                 Latitude of the gym.
lng                 Longitude of the gym.
lat_5               Latitude of the gym, truncated to 5 decimal places.
lng_5               Longitude of the gym, truncated to 5 decimal places.
distance            Distance of the gym from the set location.
direction           Cardinal direction of the gym, from the set location.
gmaps               Google Maps link to the location of the gym.
applemaps           Apple Maps link to the location of the gym.
waze                Waze link to the location of the gym.
geofence            Geofence around the event.
=================== =========================================================
