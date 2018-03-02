Stops
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

The ``"stops"`` section has three distinct settings.

+----------------------+-----------------------------------------------------------+
| Setting Name         | Description                                               |
+======================+===========================================================+
| enabled              | Process Stop Events only if ``true``                      |
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
min_time_left   Minimum time (in seconds) until monster despawns.      ``1000``
max_time_left   Maximum time (in seconds) until monster despawns.      ``2400``
geofences       See :ref:`geofences_filters` page on 'Geofences'       ``["geofence1","geofence2"]``
custom_dts      See :ref:`custom_dts_filters` page on 'Custom DTS'     ``{"dts1":"substitution"}``
is_missing_info See :ref:`missing_info_filters` page on 'Missing Info' ``true`` or ``false``
=============== ====================================================== ==============================

+ Floats can use ``"inf"`` to represent infinity
