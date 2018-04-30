Events
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:

Prerequisites
-------------------------------------

This guide assumes the following:

+ You are using the latest version of PokeAlarm.

Introduction
-------------------------------------

In PokeAlarm, an **Event** represents something of interest that has happened
in the World. Events can be several different things - a new monster spawning,
a gym changing teams, or a new raid appearing. There are 5 different categories
for Events, each with different information:

.. toctree::
   :maxdepth: 1

   monster-events
   stop-events
   gym-events
   egg-events
   raid-events
   weather-events

.. _events_dts:

Dynamic Text Substitutions
-------------------------------------

Dynamic Text Substitutions (or DTS) are special text that can be used to
customize notifications based on the triggered Event. These values are
surrounded with diamond brackets (``<`` and ``>``) and will by substituted with
a value based on the Event in question. For example, a notification with the
following text:

.. code-block:: none

     A wild <mon_name> has appeared! It has <iv>% IVs!

Could be substituted to the following:

.. code-block:: none

    A wild Charmander has appeared! It has 100.0% IVs!

Or, it could appear like this:

.. code-block:: none

     A wild Pidgey has appeared! It has 55.6% IVs!

The DTS that you can use vary by type of Event - make sure to check the page for
each type to which DTS can be used.


Missing Information
-------------------------------------

.. note:: You can accept or reject an event based on the state of missing
          information. See the ``is_missing_info`` restriction on the
          :doc:`../filters/index` page for instructions.

When PA doesn't have the correct information needed to correctly do a
substitution, it may replace it with one of the following:

+ ?
+ ???
+ unknown

This can happen for a variety of reasons - but generally is because the scanner
did not send the information needed in the webhook. PA does it's best to fill in
the gaps by sharing and caching information between separate webhooks (like gym
names or teams), but some info may require a settings update with your scanner
(like IVs or CP).


Advanced
-------------------------------------


Reverse Geocoding
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Reverse Geocoding** is a process that to get the name or data of
places where the Events take place. This can be used to get things such
as address, city, state, or more.

PA will only use Reverse Geocoding for Events that have been triggered.
Each Event will use up a single point of your API quota, regardless
of number of fields or alarms used.

================== ========================================================
Text               Description
================== ========================================================
``<street_num>``   Street number of the alert location
``<street>``       Street name of the alert location
``<address>``      Address of the alert location, includes both street
                   number and street name, in that order only
``<address_eu>``   Address of the alert location, in european format (street
                   name and street number)
``<postal>``       Postal code of the alert location
``<neighborhood>`` Neighborhood code of the alert location
``<sublocality>``  Sublocality code of the alert location
``<city>``         City code of the alert location
``<county>``       County code of the alert location
``<state>``        State code of the alert location
``<country>``      Country code of the alert location
================== ========================================================


Distance Matrix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Distance Matrix** calculations determine how far away an Event is, for
both time and distance. This can be Walking, Biking, Driving, or Transit.
These calculations require a set location, and a Google Maps API key. For more
information, see the Distance Matrix section of the
:doc:`../../miscellaneous/location-services` page.

======================= ========================================================
Text                    Description
======================= ========================================================
``<walking_distance>``  Estimated walking distance to the alert location
``<walking_duration>``  Estimated walking time to alert location
``<biking_distance>``   Estimated bike distance to the alert location
``<biking_duration>``   Estimated bike time to alert location
``<driving_distance>``  Estimated drive distance to the alert location
``<driving_duration>``  Estimated drive time to alert location
``<transit_distance>``  Estimated public transit distance to the alert location
``<transit_duration>``  Estimated public transit time to alert location
======================= ========================================================
