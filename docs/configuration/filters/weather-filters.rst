Weather
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

The ``"weather"`` section has three distinct sections.

+----------------------+-----------------------------------------------------------+
| Setting Name         | Description                                               |
+======================+===========================================================+
| enabled              | Process Weather Events only if ``true``                   |
+----------------------+-----------------------------------------------------------+
| defaults             | Section for the default settings                          |
+----------------------+-----------------------------------------------------------+
| filters              | See below parameters                                      |
+----------------------+-----------------------------------------------------------+


Available DTS
-------------------------------------

Miscellaneous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=============== ====================================================== ==============================
Parameter       Description                                            Example
=============== ====================================================== ==============================
min_dist        Min distance of event from set location in miles       ``0.0`` *
                or meters (depending on settings).
max_dist        Max distance of event from set location in miles       ``1000.0`` *
                or meters (depending on settings).
geofences       See :ref:`geofences_filters` page on 'Geofences'       ``["geofence1","geofence2"]``
custom_dts      See :ref:`custom_dts_filters` page on 'Custom DTS'     ``{"dts1":"substitution"}``
weather         A list of weather by name or ids.                      ``["Clear", 2]``
day_or_night    A list of the time of day by id or name                ``["Day", 2]``
severity        A list of weather severity by id or name               ``["None", 1, "Extreme"]``
                Note: can only be ``0``, ``1``, or ``3``
                (and the representing names)
=============== ====================================================== ==============================

+ Floats can use ``"inf"`` to represent infinity
