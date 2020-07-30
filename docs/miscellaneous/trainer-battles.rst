PvP / Trainer Battles
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:


The relevance of stat product
-------------------------------------

If you want to narrow down the potential of a Pokemon for the
great and ultra leagues of Trainer Battles, it's not as easy
as for raid battles or the master league. In these situations,
you simply always want the highest possible IVs for all categories.

Great and ultra league are of their own kind with their respective
CP ceilings, however. With TDO (total damage output`_ being
widely considered as the best measurement of a Pokemons raw
potential in great and ultra league, you'll want to look at stat
product, because TDO directly scales with it.

This is because of the fact that the CP formula applies higher
weight to the ATK stat over the DEF and STA stats, so lower ATK
Pokemon can have a advantage in these capped leagues: you can
potentially cram more stat product below the CP ceiling by
trading off some ATK for higher amounts of DEF or STA.

There's a number of in-depth articles available on the internet,
for example `this analysis on gamepress.gg <https://gamepress.gg/pokemongo/analysis-ideal-iv-sets-pokemon-go-pvp>`_.

At `gostadium.club <https://gostadium.club/pvp/iv>`_, you can
put in a Pokemon and its IV combination and find out how it
ranks among all possible alternatives of its species.


Implementation in PokeAlarm
-------------------------------------

With the PvP feature, PokeAlarm brings the perfect stat product
for each individual Pokemon for both great and ultra leagues as
a new, pre-calculated base stat.

For every Mon event, it will calculate the individual Pokemon's
maximum stat product and the corresponding level and CP value.
It'll then express this stat product as a percentage of the
perfect stat product.

If the Pokemon has possible evolutions, the same values will
be calculated for the evolved forms and finally, the values
of the evolution stage that is the closest to 100% will be chosen
and returned with the related DTS strings and filter values.

The calculations will also take into account that it is not
possible for a Pokemon to lose levels, so higher evolution
forms will only be used if the wild Pokemon is not beyond
the level that would be required for the respective league.


DTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's examine a `wild Level 24, 1/15/15 Scyther <https://gostadium.club/pvp/iv?pokemon=Scyther&max_cp=2500&min_iv=0&att_iv=1&def_iv=15&sta_iv=15>`_ in ultra league.
Its stat product will be 99.42% of the perfect 0/13/15 Scyther
with 2489 CP at level 38.5.

`Evolved to Scizor <https://gostadium.club/pvp/iv?pokemon=Scizor&max_cp=2500&min_iv=0&att_iv=1&def_iv=15&sta_iv=15>`_,
this same Pokemon would only reach 98.90% of the perfect 
0/15/15 Scizor at 2489 CP and level 31.5.

In this case, the final result would return the values
of the superior Scyther. This means that the ultra league
DTS would be as follows:

=============== ==========
DTS             Content
=============== ==========
ultra_product   ``99.42%``
ultra_mon_name  ``Scyther``
ultra_cp        ``2489``
ultra_level     ``38.5``
ultra_url       ``https://gostadium.club/pvp/iv?pokemon=Scyther&max_cp=2500&min_iv=0&att_iv=1&def_iv=15&sta_iv=15``
=============== ==========

Now, consider a `wild level 24, 0/14/13 Scyther <https://gostadium.club/pvp/iv?pokemon=Scyther&max_cp=2500&min_iv=0&att_iv=0&def_iv=14&sta_iv=13>`_ for ultra league.
It would score a stat product percentage of 99.18%, while
`the corresponding Scizor <https://gostadium.club/pvp/iv?pokemon=Scizor&max_cp=2500&min_iv=0&att_iv=0&def_iv=14&sta_iv=13>`_
would reach 99.57%.

This means that in this case, the return values would
be those of the resulting Scizor:

=============== ==========
DTS             Content
=============== ==========
ultra_product   ``99.57%``
ultra_mon_name  ``Scizor``
ultra_cp        ``2499``
ultra_level     ``32.5``
ultra_url       ``https://gostadium.club/pvp/iv?pokemon=Scizor&max_cp=2500&min_iv=0&att_iv=0&def_iv=14&sta_iv=13>``
=============== ==========


Filters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The added filters, as listed in the Filters section, should
not be too hard to understand. They make use of the calculated
``great_product`` and ``ultra_product``, and ``great_cp`` and 
``ultra_cp`` respectively, to be able to filter by stat product
percentage and to cut off results that are perfect in principle,
but too low in CP to be actually usable in the chosen league.

``min_great`` and ``min_ultra`` will define a stat product
percentage floor, ``max_great`` and ``max_ultra`` a stat
product percentage ceiling. ``min_cp_great`` and ``min_cp_ultra``
will define a CP floor.
