Invasions
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:

Prerequisites
-------------------------------------

This page assumes:

+ You have a working scanner.
+ You understand
  `JSON formatting <https://www.w3schools.com/js/js_json_intro.asp>`_.
+ You are using the latest version of PokeAlarm.
+ You have read and understood the :doc:`index` page.

Introduction
-------------------------------------

The ``"invasions"`` section has three distinct settings.

+----------------------+-----------------------------------------------------------+
| Setting Name         | Description                                               |
+======================+===========================================================+
| enabled              | Process Invasion Events only if ``true``                  |
+----------------------+-----------------------------------------------------------+
| defaults             | Section for the default settings                          |
+----------------------+-----------------------------------------------------------+
| filters              | See below parameters                                      |
+----------------------+-----------------------------------------------------------+


Available DTS
-------------------------------------

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=================== ============================================================== ===============================
Parameter           Description                                                    Example
=================== ============================================================== ===============================
grunt_ids           Array of allowed grunts, by id.                                ``["4", 39]``
grunts_exclude      Array of excluded grunts, by id.                               ``["4", 39]``
grunt_genders       Array of allowed genders, by id or name.                       ``["Male", 2]``
types               Array of allowed monster types, by name.                       ``["Dark", "Dragon", "Grass"]`` 
monsters            Array of allowed monsters possibly rewarded, by  or name.      ``["Bulbasaur","2",3]``
monsters_exclude    Array of excluded monsters possibly rewarded, by id or name.   ``["Bulbasaur","2",3]``
=================== ============================================================== ===============================


Miscellaneous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=================== ================================================================ ==============================
Parameter           Description                                                      Example
=================== ================================================================ ==============================
min_dist            Min distance of event from set location in miles                 ``0.0`` *
                    or meters (depending on settings).
max_dist            Max distance of event from set location in miles                 ``1000.0`` *
                    or meters (depending on settings).
min_time_left       Minimum time (in seconds) until monster despawns.                ``1000``
max_time_left       Maximum time (in seconds) until monster despawns.                ``2400``
weather             Accepted weather conditions, by id or name.                      ``["Clear",2]``
boosted_weather     Accepted boosted weather conditions, by id or name.               ``["Clear",2]``
is_boosted_weather  Accepts or denies based on boosted weather conditions.           ``true``
geofences           See :ref:`geofences_filters` page on 'Geofences'                 ``["geofence1","geofence2"]``
exclude_geofences   Opposite of `geofences`. See :ref:`geofences_filters` page.      ``["geofence1","geofence2"]``
min_time            See :ref:`time_dts_filters` page on 'Time DTS'                   ``8:30``
max_time            See :ref:`time_dts_filters` page on 'Time DTS'                   ``22:00``
custom_dts          See :ref:`custom_dts_filters` page on 'Custom DTS'               ``{"dts1":"substitution"}``
is_missing_info     See :ref:`missing_info_filters` page on 'Missing Info'           ``true`` or ``false``
=============== ==================================================================== ==============================

+ Floats can use ``"inf"`` to represent infinity
