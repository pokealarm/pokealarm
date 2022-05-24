Quests
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

The ``"quest"`` section has three distinct settings.

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

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================== ======================================== ====================================
Parameter          Description                              Example
================== ======================================== ====================================
stop_name_contains Array of allowed stop names              ``["Monster HQ", "Eiffel Tower"]``
                   - Allows regex
stop_name_excludes Array of excluded stop names             ``["Private Property", "Somewhere"``
                   - Allows regex
template_contains  Array of allowed template names          ``["T3_2019_FRIENDS_TRADE"]``
                   - Allows regex
template_excludes  Array of excluded template names         ``["T3_2019_FRIENDS_TRADE"]``
                   - Allows regex
task_contains      Array of allowed task strings            ``["Catch", "Dragonite"]``
task_excludes      Array of excluded task strings           ``["Battle", "Berry"]``
reward_types       Array of allowed reward types - See the  ``["Monster Encounter", "3", 2]``
                   table below for allowed types
min_reward_amount  Minimum amount of the reward             ``5``
max_reward_amount  Maximum amount of the reward             ``3000``
================== ======================================== ====================================

+ When the reward is a monster, the reward amount is always 1

Monster Rewards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================== =============================================== ====================================
Parameter          Description                                     Example
================== =============================================== ====================================
monsters           Array of allowed monsters, by id or name.       ``["Bulbasaur","2",3]``
monsters_exclude   Array of excluded monsters, by id or name.      ``["Bulbasaur","2",3]``
form_ids           Array of allowed form ids for a monster.        ``[0,"1"]``
costume_ids        Array of allowed costume ids for a monster      ``[0,"1"]``
types              Array of allowed monster types, by name.        ``["Dark", "Dragon", "Grass"]``
can_be_shiny       Accepts or denies based on shiny availability.  ``true`` or ``false``
================== =============================================== ====================================

Item Rewards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================== ========================================== ====================================
Parameter          Description                                Example
================== ========================================== ====================================
items              Array of allowed items, by id or name.     ``["Great Ball", 104, "707"]``
                   See below table for allowed items.
items_exclude      Array of excluded items, by id or name.    ``["Great Ball", 104, "707"]``
                   See below table for allowed items.
================== ========================================== ====================================

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
geofences           See :ref:`geofences_filters` page on 'Geofences'                 ``["geofence1","geofence2"]``
exclude_geofences   Opposite of `geofences`. See :ref:`geofences_filters` page.      ``["geofence1","geofence2"]``
min_time            See :ref:`time_dts_filters` page on 'Time DTS'                   ``8:30``
max_time            See :ref:`time_dts_filters` page on 'Time DTS'                   ``22:00``
custom_dts          See :ref:`custom_dts_filters` page on 'Custom DTS'               ``{"dts1":"substitution"}``
is_missing_info     See :ref:`missing_info_filters` page on 'Missing Info'           ``true`` or ``false``
=================== ================================================================ ==============================

+ Floats can use ``"inf"`` to represent infinity


Reward Types
-------------------------------------
==== =================
ID   Name
==== =================
0    Unset
1    Experience
2    Item
3    Stardust
4    Candy
5    Avatar Clothing
6    Quest
7    Monster Encounter
==== =================

+ Currently in a real application, you'll only see quests for items, stardust, and monster encounters

Items
-------------------------------------

===== =======================
ID    Name
===== =======================
0     Unknown
1     Poké Ball
2     Great Ball
3     Ultra Ball
4     Master Ball
5     Premier Ball
101   Potion
102   Super Potion
103   Hyper Potion
104   Max Potion
201   Revive
202   Max Revive
301   Lucky Egg
401   Incense
402   Spicy Incense
403   Cool Incense
404   Floral Incense
405   Mystery Box
501   Lure Module
502   Glacial Lure Module
503   Mossy Lure Module
504   Magnetic Lure Module
602   X-Attack
603   X-Defense
604   X-Miracle
701   Razz Berry
702   Bluk Berry
703   Nanab Berry
704   Wepar Berry
705   Pinap Berry
706   Golden Razz Berry
707   Golden Nanab Berry
708   Silver Pinap Berry
709   Poffin
801   Camera
901   Unlimited Incubator
902   Incubator
903   Super Incubator
1001  Pokemon Storage Upgrade
1002  Item Storage Upgrade
1101  Sun Stone
1102  Kings Rock
1103  Metal Coat
1104  Dragon Scale
1105  Up Grade
1106  Sinnoh Stone
1107  Unova Stone
1201  Fast TM
1202  Charge TM
1301  Rare Candy
1401  Free Raid Pass
1402  Paid Raid Pass
1403  Legendary Raid Pass
1404  Star Piece
1405  Gift
1406  Team Change Medallion
1501  Leader Map Fragment
1502  Leader Map
1503  Giovanni Map
1600  Global Event Ticket
===== =======================

+ Not all of these items will be available through quests, although you could filter by any of them
+ Also, some of these items do not have images since they are not yet released