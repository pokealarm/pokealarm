Monsters
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

A **Monster Event** represents when a monster spawns in the wild.


Available DTS
-------------------------------------

General
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

========================== ==========================================================
DTS                        Description
========================== ==========================================================
mon_name                   The name of the monster's species.
mon_id                     ID of the monster's species.
mon_id_3                   ID of the monster's species, padded to 3 digits.
form                       Form name of the monster.
form_or_empty              Form name of the monster, or empty string if unknown.
nonnormal_form_or_empty    Form name of the monster, or empty string if Normal or unknown.
form_id                    Form ID for the monster.
form_id_2                  Form ID of the monster, padded to 2 digits.
form_id_3                  Form ID of the monster, padded to 3 digits.
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
========================== ==========================================================


Stats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    The DTS in this section require your scanner to encounter the target
    monsters to get the proper information. This typically requires special
    settings and accounts - see the documentation for your scanner for
    specifics.

===================== =========================================================
DTS                   Description
===================== =========================================================
mon_lvl               Level of the monster.
cp                    Combat Points of the monster.
iv                    Individual Values percentage of the monster.
iv_0                  IVs, rounded to the nearest integer.
iv_2                  IVs, rounded to 2 decimal places.
atk                   Attack IV of the monster.
def                   Defense IV of the monster.
sta                   Stamina IV of the monster.
max_cp                Final CP after maxing out the monster.
max_perfect_cp        Final CP after maxing out a perfect IV monster.
max_evo_cp            Final CP after evolving and maxing out the monster.
max_perfect_evo_cp    Final CP after evolving and maxing out a perfect IV monster.
stardust_cost         Stardust cost to power up the monster to its max level.
candy_cost            Candy cost to power up the monster to its max level.
candy_cost_with_evo   Candy cost to evolve and power up the monster to its max level.
base_catch            Catch rate of the monster when using a poke ball.
base_catch_0          Catch rate of the monster when using a poke ball, rounded to the nearest integer.
base_catch_2          Catch rate of the monster when using a poke ball, rounded to 2 decimal places.
great_catch           Catch rate of the monster when using a great ball.
great_catch_0         Catch rate of the monster when using a great ball, rounded to the nearest integer.
great_catch_2         Catch rate of the monster when using a great ball, rounded to 2 decimal places.
ultra_catch           Catch rate of the monster when using an ultra ball.
ultra_catch_0         Catch rate of the monster when using an ultra ball, rounded to the nearest integer.
ultra_catch_2         Catch rate of the monster when using an ultra ball, rounded to 2 decimal places.
rarity                Rarity of the monster, as supplied by the scanner.
===================== =========================================================

Moves
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    The DTS in this section require your scanner to encounter the target
    monsters to get the proper information. This typically requires special
    settings and accounts - see the documentation for your scanner for
    specifics.

=================== =========================================================
DTS                 Description
=================== =========================================================
quick_move          Name of the monster's quick move.
quick_id            ID of the monster's quick move.
quick_type_id       ID of the monster's quick move type.
quick_type          Name of the monster's quick move type.
quick_type_emoji    Emoji of the monster's quick move type.
quick_damage        Damage of the monster's quick move.
quick_dps           DPS of the monster's quick move.
quick_duration      Duration of the monster's quick move.
quick_energy        Energy generated by the quick move.
charge_move         Name of the monster's charge move.
charge_id           ID of the monster's charge move.
charge_type_id      ID of the monster's charge move type.
charge_type         Name of the monster's charge move type.
charge_type_emoji   Emoji of the monster's charge move type.
charge_damage       Damage of the monster's charge move.
charge_dps          DPS of the monster's charge move.
charge_duration     Duration of the monster's charge move.
charge_energy       Energy generated by the charge move.
atk_grade           Offensive grade of the monster's moveset.
def_grade           Defensive grade of the monster's moveset.
=================== =========================================================

PvP / Trainer Battles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    The DTS in this section require your scanner to encounter the target
    monsters to get the proper information. This typically requires special
    settings and accounts - see the documentation for your scanner for
    specifics.

.. note::
    A more detailed explanation about the Trainer Battle calculations
    and the resulting DTS can be found in :doc:`../../miscellaneous/trainer-battles`.

=================== =========================================================
DTS                 Description
=================== =========================================================
great_mon_id        The ID of the monster or its evolution that reaches the highest stat product in great league
great_product       Highest stat product percentage the mon or its evolution can reach in great league
great_mon_name      Name of the mon or its evolution that reaches the highest stat product in great league
great_cp            CP at the highest possible level in great league for the mon or its evolution
great_level         The level at which the mon will reach the highest possible CP in great league
great_candy         Candy cost to power up the mon or its evolution in great league
great_stardust      Stardust cost to power up the mon or its evolution in great league
great_rank          The current rank of the monster in great league
great_url           Individual link to gostadium.club to further analyze the mon or its evolution in great league
great_pvpoke        Individual link to pvpoke.com to further analyze the mon or its evolution in great league
ultra_mon_id        The ID of the monster or its evolution that reaches the highest stat product in ultra league
ultra_product       Highest stat product percentage the mon or its evolution can reach in ultra league
ultra_mon_name      Name of the mon or its evolution that reaches the highest stat product in ultra league
ultra_cp            CP at the highest possible level in ultra league for the mon or its evolution
ultra_level         The level at which the mon will reach the highest possible CP in ultra league
ultra_candy         Candy cost to power up the mon or its evolution in ultra league
ultra_stardust      Stardust cost to power up the mon or its evolution in ultra league
ultra_rank          The current rank of the monster in ultra league
ultra_url           Individual link to gostadium.club to further analyze the mon or its evolution in ultra league
ultra_pvpoke        Individual link to pvpoke.com to further analyze the mon or its evolution in ultra league
=================== =========================================================

Cosmetic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    The DTS in this section require your scanner to encounter the target
    monsters to get the proper information. This typically requires special
    settings and accounts - see the documentation for your scanner for
    specifics.

=================== ============================================================
DTS                 Description
=================== ============================================================
costume             Costume of the monster.
costume_or_empty    Costume of the monster, or an empty string if unknown.
costume_id          Costume ID of the monster.
costume_id_2        Costume ID of the monster, padded to 2 digits.
costume_id_3        Costume ID of the monster, padded to 3 digits.
gender              Gender of the monster, represented as a single character.
height              Height of the monster.
height_0            Height of the monster, rounded to the nearest integer.
height_2            Height of the monster, rounded to 2 decimal places.
weight              Weight of the monster.
weight_0            Weight of the monster, rounded to the nearest integer.
weight_2            Weight of the monster, rounded to 2 decimal places.
size                Estimated size of the monster.
big_karp            Return `big` if Magikarp weight is >=13.13.
tiny_rat            Return `tiny` if Rattata weight is <=2.41.
=================== ============================================================

Ditto disguise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

    The DTS in this section are only relevant if your scanner encountered a
    Ditto. This allows you to know information on the monster displayed in the overworld.

======================= ============================================================================
DTS                     Description
======================= ============================================================================
display_mon_name        Name of the displayed monster.
display_mon_id          ID of the displayed monster.
display_mon_id_2        ID of the displayed monster, padded to 2 digits.
display_mon_id_3        ID of the displayed monster, padded to 3 digits.
display_costume         Name of the displayed monster's costume.
display_costume_id      ID of the displayed monster's costume.
display_costume_id_2    ID of the displayed monster's costume, padded to 2 digits.
display_costume_id_3    ID of the displayed monster's costume, padded to 3 digits.
display_form            Name of the displayed monster's form.
display_form_id         ID of the displayed monster's form.
display_form_id_2       ID of the displayed monster's form, padded to 2 digits.
display_form_id_3       ID of the displayed monster's form, padded to 3 digits.
display_gender          Gender of the displayed monster, represented as a single character.
======================= ============================================================================

Location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Geofences are evaluated on a per Filter basis - ``<geofence>`` will
    always be unknown if it passes through a Filter without a ``geofences``
    restriction applied.

=================== ============================================================
DTS                 Description
=================== ============================================================
distance            Distance of the monster from the set location.
direction           Cardinal direction of the monster, from the set location.
lat                 Latitude of the monster.
lng                 Longitude of the monster.
lat_5               Latitude of the monster, truncated to 5 decimal places.
lng_5               Longitude of the monster, truncated to 5 decimal places.
gmaps               Google Maps link to the location of the monster.
gnav                Google Maps Navigation to the location of the monster.
applemaps           Apple Maps link to the location of the monster.
applenav            Apple Maps Navigation to the location of the monster.
waze                Waze link to the location of the monster.
wazenav             Waze Navigation to the location of the monster.
geofence            Geofence around the monster.
=================== ============================================================


Time
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

===================== ======================================================================= ============
DTS                   Description                                                             Example
===================== ======================================================================= ============
time_left             Time remaining until the monster expires.                               1h 15m 52s
12h_time              Time that the monster will disappear, in a 12h format.                  01:15:52pm
24h_time              Time that the monster will disappear, in a 24h format.                  13:15:52
time_left_no_secs     Time remaining until the monster expires without seconds.               1h 15m
12h_time_no_secs      Time that the monster will disappear, in a 12h format, without seconds. 01:15pm
24h_time_no_secs      Time that the monster will disappear, in a 24h format, without seconds. 13:15
time_left_raw_hours   Hours only until the monster expires.                                   1
time_left_raw_minutes Minutes only until the monster expires.                                 15
time_left_raw_seconds Seconds only until the monster expires.                                 52
===================== ======================================================================= ============


Weather
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

======================== =======================================================
DTS                      Description
======================== =======================================================
weather_id               Weather ID of the monster.
weather                  Weather name of the monster.
weather_or_empty         Weather name of the monster, or empty string if
                         unknown.
weather_emoji            Weather emoji of the monster, or empty string if
                         unknown.
boosted_weather_id       Return weather ID if monster is boosted.
boosted_weather          Return weather name if monster is boosted.
boosted_weather_or_empty Return weather name if monster is boosted, or
                         empty string if unknown.
boosted_weather_emoji    Return weather emoji if monster is boosted, or
                         empty string if unknown.
boosted_or_empty         Return `boosted` if monster is boosted, or empty
                         string if not.
======================== =======================================================


Miscellaneous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=============================== ===================================================================================================
DTS                             Description
=============================== ===================================================================================================
encounter_id                    The encounter id. Unique per monster spawn.
spawnpoint_id                   Return the spawnpoint ID that the monster spawned on.
spawn_start                     Estimated time that the monster spawn starts.
spawn_end                       Estimated time that the monster spawn ends.
spawn_verified                  *True* or *False* based on if spawns have been verified.
spawn_verified_emoji            An unknown (❔), verified (✅), or unverified (❌) emoji based on if spawns have been verified.
spawn_verified_emoji_or_empty   When the spawn is verified, this gives the above verified emoji. Otherwise, it will be empty.
spawn_unverified_emoji_or_empty When the spawn is not verified, this gives the above unverified emoji. Otherwise, it will be empty.
=============================== ===================================================================================================
