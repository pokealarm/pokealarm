Gyms
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

The ``"gyms"`` section has four distinct settings.

+----------------------+-----------------------------------------------------------+
| Setting Name         | Description                                               |
+======================+===========================================================+
| enabled              | Process Gym Events only if ``true``                       |
+----------------------+-----------------------------------------------------------+
| ignore_neutral       | If ``true``, ignore uncontested gyms                      |
+----------------------+-----------------------------------------------------------+
| defaults             | Section for the default settings                          |
+----------------------+-----------------------------------------------------------+
| filters              | See below parameters                                      |
+----------------------+-----------------------------------------------------------+


Available DTS
-------------------------------------

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================== ================================================ ================================
Parameter          Description                                      Example
================== ================================================ ================================
old_teams          List of allowed previous teams, by id or name.   ``["Instinct","Mystic"]``
new_teams          List of allowed new teams, by id or name.        ``["Valor","Mystic"]``
gym_name_contains  List of regex's required to be in the gym name.  ``["Sponsored","West\\sOak"]``
gym_name_excludes  List of regex's rejected to be in the gym name.  ``["Sponsored","West\\sOak"]``
min_slots          Minimum number of guard slots available.         ``2``
max_slots          Maximum number of guard slots available.         ``6``
park_contains      List of regex's required to be in the park name. ``["Sponsored","Park\\sName"]``
sponsored          restrict sponsor_id to be zero or not            ``true`` or ``false``
================== ================================================ ================================


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
is_missing_info See :ref:`missing_info_filters` page on 'Missing Info' ``true`` or ``false``
=============== ====================================================== ==============================

+ Floats can use ``"inf"`` to represent infinity
