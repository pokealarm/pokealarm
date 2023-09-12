Monsters
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

The ``"monsters"`` section has three distinct settings.

+----------------------+-----------------------------------------------------------+
| Setting Name         | Description                                               |
+======================+===========================================================+
| enabled              | Process Monster Events only if ``true``                   |
+----------------------+-----------------------------------------------------------+
| defaults             | Section for the default settings                          |
+----------------------+-----------------------------------------------------------+
| filters              | See below parameters                                      |
+----------------------+-----------------------------------------------------------+


Available DTS
-------------------------------------

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=================== ================================================================ ================================
Parameter           Description                                                      Example
=================== ================================================================ ================================
monsters            Array of allowed monsters, by ID or name.                        ``["Bulbasaur","2",3]``
monsters_exclude    Array of excluded monsters, by ID or name.                       ``["Bulbasaur","2",3]``
form_ids            Array of allowed form IDs for the monster.                       ``[0,"1"]``
exclude_forms       Array of excluded forms, by ID.                                  ``[0,"1"]``
costume_ids         Array of allowed costume IDs for the monster.                    ``[0,"1"]``
exclude_costumes    Array of excluded costumes, by ID.                               ``[0,"1"]``
exclude_geofences   Opposite of `geofences`. See :ref:`geofences_filters` page.      ``["geofence1","geofence2"]``
types               Array of allowed monster types, by name.                         ``["Dark", "Dragon", "Grass"]``
genders             Array of acceptable genders. Options: `"male",                   ``["female"]``
                    "female", "neutral"`
rarity              Array of allowed rarities.                                       ``["common", "uncommon", 3``
can_be_shiny        Accepts or denies based on shiny availability.                   ``true`` or ``false``
=================== ================================================================ ================================


Encounter Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    Encounter information may require special settings or accounts for your
    scanner to work correctly. Please consult the documentation for your
    scanner.

============== ================================================== ================================
Parameter      Description                                        Example
============== ================================================== ================================
min_lvl        Minimum level of the monster.                      ``0``
max_lvl        Maximum level of the monster.                      ``40``
min_atk        Minimum attack IV of the monster.                  ``0``
max_atk        Maximum attack IV of the monster.                  ``15``
min_def        Minimum defense IV of the monster.                 ``0``
max_def        Maximum defense IV of the monster.                 ``15``
min_sta        Minimum stamina IV of the monster.                 ``0``
max_sta        Maximum stamina IV of the monster.                 ``15``
min_iv         Minimum total IV percentage of the monster.        ``0.0`` *
max_iv         Maximum total IV percentage of the monster.        ``100.0`` *
min_cp         Minimum CP of the monster.                         ``0``
max_cp         Maximum CP of the monster.                         ``10000``
quick_moves    Accepted quick moves, by ID or name.               ``["Vine Whip","Tackle"]``
charge_moves   Accepted charge moves, by ID or name.              ``["Sludge Bomb","Seed Bomb"]``
min_height     Minimum height of the monster.                     ``0.0`` *
max_height     Maximum height of the monster.                     ``250.0`` *
min_weight     Minimum weight of the monster.                     ``0.0`` *
max_weight     Maximum weight of the monster.                     ``250.0`` *
sizes          Array of acceptable sizes. Options: `"tiny",       ``["tiny","big"]``
               "small", "normal", "large", "big"`
============== ================================================== ================================


PvP / Trainer Battles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
    A more detailed explanation about the Trainer Battle calculations
    and the resulting DTS can be found in :doc:`../../miscellaneous/trainer-battles`.
    Trainer Battle calculations also require encounter information - see
    the note above.

=============== =============================================================== ==============================
Parameter       Description                                                     Example
=============== =============================================================== ==============================
min_great       Minimum stat product percentage of the mon for great league     ``95``
max_great       Maximum stat product percentage of the mon for great league     ``99``
min_cp_great    Minimum resulting great league CP for the mon                   ``1300``
min_rank_great  Minimum current rank of the mon for great league                ``1``
max_rank_great  Maximum current rank of the mon for great league                ``50``
min_ultra       Minimum stat product percentage of the mon for ultra league     ``95``
max_ultra       Maximum stat product percentage of the mon for ultra league     ``99``
min_cp_ultra    Minimum resulting ultra league CP for the mon                   ``1300``
min_rank_ultra  Minimum current rank of the mon for ultra league                ``1``
max_rank_ultra  Maximum current rank of the mon for ultra league                ``50``
=============== =============================================================== ==============================


Miscellaneous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================== ====================================================== ==============================
Parameter          Description                                            Example
================== ====================================================== ==============================
min_dist           Min distance of event from set location in miles       ``0.0`` *
                   or meters (depending on settings).
max_dist           Max distance of event from set location in miles       ``1000.0`` *
                   or meters (depending on settings).
min_time_left      Minimum time (in seconds) until monster despawns.      ``1000``
max_time_left      Maximum time (in seconds) until monster despawns.      ``2400``
weather            Accepted weather conditions, by ID or name.            ``["Clear",2]``
boosted_weather    Accepted boosted weather conditions, by ID or name.     ``["Clear",2]``
is_boosted_weather Accepts or denies based on boosted weather conditions. ``true``
geofences          See :ref:`geofences_filters` page on 'Geofences'       ``["geofence1","geofence2"]``
min_time           See :ref:`time_dts_filters` page on 'Time DTS'         ``8:30``
max_time           See :ref:`time_dts_filters` page on 'Time DTS'         ``22:00``
custom_dts         See :ref:`custom_dts_filters` page on 'Custom DTS'     ``{"dts1":"substitution"}``
is_missing_info    See :ref:`missing_info_filters` page on 'Missing Info' ``true`` or ``false``
================== ====================================================== ==============================

+ Floats can use ``"inf"`` to represent infinity
