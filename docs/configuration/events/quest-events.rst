Quests
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

A **Quest Event** represents when a quest appears in a pokestop.

This currently only works with one scanner.

.. note::
     If you're unsure as to which reward type your alarm will be reporting, use the generic 
     `reward` DTS, this will make it so you don't have any unused or unnecessary space

.. warning::
    Monster and item information is always sent with defaults, so including DTS
    for these when it's actually a different reward type will show misleading information.


Available DTS
-------------------------------------

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= ========================================================
DTS               Description
================= ========================================================
quest_type        The type of quest - raw data from the scanner in words.
quest_type_id     The ID of the quest type
quest_target      The target of the quest
quest_task        The compiled task from the scanner in words
quest_template    The in-game quest campaign template - usually for events
quest_condition   The conditions of the quest - raw data from the scanner
                  in words - will be changed to interpreted later.
quest_image       The relative image based on the quest reward.
                  See below for more information.
================= ========================================================

quest_image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The `quest_image` will be one of the following based on the reward type
* When the type is a monster, this will link to the appropriate monster image
* When the type is an item, this will link to the appropriate item image
* When the type is anything else (such as stardust), this will link to the generic image for that type

Reward Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= ==============================================================
DTS               Description
================= ==============================================================
reward            The amount and reward information in detail
                  - changed per locale
reward_type_id    The ID of the reward type, see :doc:`../filters/quest-filters`
                  for more info
reward_type       The reward type name
reward_type_raw   The name of the reward interpreted by the scanner
reward_amount     The amount of the reward
================= ==============================================================

Monster Reward Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

========================== ========================================================
DTS                        Description
========================== ========================================================
mon_id                     The ID of the monster
mon_name                   The name of the monster's species.
mon_id                     ID of the monster's species.
mon_id_3                   ID of the monster's species, padded to 3 digits.
form                       Form name of the monster.
form_or_empty              Form name of the monster, or empty string if unknown.
nonnormal_form_or_empty    Form name of the monster, or empty string if Normal or unknown.
form_id                    Form ID for the monster.
form_id_3                  Form ID of the monster, padded to 3 digits.
costume                    The name of the monster's costume.
costume_or_empty           The name of the monsters costume or an empty string if
                           unknown.
costume_id                 The costume ID of the monster.
costume_id_2               The costume ID of the monster, padded to 2 digits.
costume_id_3               The costume ID of the monster, padded to 3 digits.
type1                      Name of the monster's primary type.
type1_or_empty             Name of the monster's primary type, or empty string
                           if unknown.
type1_emoji                Emoji for the monster's primary type, or empty string
                           if unknown.
type2                      Name of the monster's secondary type.
type2_or_empty             Name of the monster's secondary type, or empty string
                           if unknown.
type2_emoji                Emoji for the monster's secondary type, or empty string
                           if unknown.
types                      Monster's type formatted as "type1/type2".
types_emoji                Type emojis for the monster as "type1+type2", or empty
                           string if unknown.
shiny_emoji                Return shiny emoji (✨) if monster can be shiny, or
                           empty string if unknown.
========================== ========================================================

Item Reward Details
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= ========================================================
DTS               Description
================= ========================================================
item              The name of the item
raw_item_type     The name of the item interpreted by the scanner
item_id           The ID of the item
item_id_4         The ID of the item padded to 4 with prepended zeros
================= ========================================================

Pokestop Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

================= ========================================================
DTS               Description
================= ========================================================
stop_id           The ID of the pokestop this quest is at
stop_name         The name of the pokestop this quest is at
stop_image        The url of the image of the pokestop
================= ========================================================


Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Geofences are only evaluated per Filter - ``<geofence>`` will be unknown if
    it passes through a Filter without a ``geofences`` restriction applied.

=================== =========================================================
DTS                 Description
=================== =========================================================
lat                 Latitude of the quest.
lng                 Longitude of the quest.
lat_5               Latitude of the quest, truncated to 5 decimal places.
lng_5               Longitude of the quest, truncated to 5 decimal places.
distance            Distance of the quest from the set location.
direction           Cardinal direction of the quest, from the set location.
gmaps               Google Maps link to the location of the quest.
gnav                Google Maps Navigation to the location of the quest.
applemaps           Apple Maps link to the location of the quest.
applenav            Apple Maps Navigation to the location of the quest.
waze                Waze link to the location of the quest.
wazenav             Waze Navigation to the location of the quest.
geofence            Geofence around the quest.
=================== =========================================================


Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

======================= =============================================================== =============
DTS                     Description                                                     Example
======================= =============================================================== =============
last_modified           Time when the quest was last marked as modified - ISO Timestamp ISO-Example_
======================= =============================================================== =============

.. _ISO-Example: https://www.isotimestamp.com/