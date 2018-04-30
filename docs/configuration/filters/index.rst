Filters
========

.. contents:: Table of Contents
   :depth: 2
   :local:


Prerequisites
-------------------------------------

This pages assumes the following:

+ You understand how :doc:`../events/index` work.
+ You understand `JSON formatting <https://www.w3schools.com/js/js_json_intro.asp>`_.
+ You are using the latest version of PokeAlarm.

Introduction
-------------------------------------

A **Filter** is what PA uses to decide if it is worth of a notification or not.
When PA receives a new Event, it is compared one by one against the Filters.
When PA finds a matching Filter, it triggers a notification.

.. note:: By default, PA processes Filters in the order they are listed in the
         filters file and only triggers on the first match. You can override
         this behavior by using the advanced :doc:`../rules-overview` feature.

There are 5 different types of Filters, each matching a category of Events:


.. toctree::
   :maxdepth: 1

   monster-filters
   stop-filters
   gym-filters
   egg-filters
   raid-filters
   weather-filters


Restrictions
-------------------------------------

A Filter is represented as a *named* JSON Object containing several key-value
pairs called *restrictions*. Each restriction represents a limit on which Events
are allowed to pass. Restrictions are *explicit* (they must be listed to be
checked) and *associative* (all restrictions must be passed to match) A Filter
with no restrictions would allow any Event to pass:

.. code-block:: json

    "all-filter-name":{
    }

.. note:: Filters will *only* check an Event's value if a restriction requires
          it. A Monster's IV value won't be checked unless either ``min_iv`` or
          ``max_iv`` is set. As such, you should avoid setting restrictions
          unless you intend to Filter on those values.

To add a ``monsters`` restriction, you simply describe it inside the object. The
following would only allow Monsters of certain species:

.. code-block:: json

    "only-starters":{
      "monsters":["Charmander","Squirtle","Bulbasaur"]
    }

Additional restrictions are added in the same way:

.. code-block:: json

    "only-high-iv-lvl-starters":{
      "monsters":["Charmander","Squirtle","Bulbasaur"],
      "min_iv": 90.0,
      "min_lvl": 15
    }

Each type of Filter has different restrictions, so make sure to check each page
carefully.

Filters File
-------------------------------------

A *filters file* (often refereed to as ``filters.json``) is a file containing
the Filters that PA uses. By default, PA loads the Filter from the
``filters.json`` located in the base folder of the project. See the
:doc:`../server-settings` page for instructions on specifying the file by
a different name. This file must contain a single JSON object to load
successfully:

.. code-block:: json

    {

    }

Inside this JSON object, you need to add sections for each type of Filter you
wish to add. Sections are optional, and unspecified sections will be disabled
by default.

.. code-block:: json

    {
      "monsters":{
      },
      "stops":{
      },
      "gyms":{
      },
      "eggs":{
      },
      "raids":{
      },
      "weather":{
      }
    }

Each section can contain the following sub-sections:

The ``enabled`` sub-section is a boolean value of either ``true`` or ``false``
that enables or disables processing of that type of Event.

The ``defaults`` sub-section is a JSON object containing default restrictions
that are applied to all Filters in the section, unless already specified. For
example, adding  ``"min_iv": 90`` in the monsters defaults section will add that
restriction to all Filters - unless they already have a ``min_iv`` restriction.

.. note:: You can use ``null`` to ignore a default value. Even with a default
          ``"monsters"`` restriction set, ``"monsters":null`` inside a filter
          acts as if that the monster restriction is not set.

The ``filters`` section is simply a JSON object containing the Filters,
configured as described above. Here is an example of just the monsters section:

.. code-block:: json

          "monsters":{
              "enabled":true,
              "defaults":{},
              "filters":{
                  "filter_by_monsters_example":{
                      "monsters":["Bulbasaur","Charmander",7]
                  },
                  "filter_by_ivs_example":{
                      "min_atk": 0, "max_atk": 15,
                      "min_iv": 0.0, "max_iv": 100
                  },
                  "filter_by_moves_example":{
                      "monsters":["Bulbasaur"],
                      "quick_moves":["Vine Whip","Tackle"],
                      "charge_moves":["Sludge Bomb","Seed Bomb"]
                  }
              }
          }


Advanced
-------------------------------------

.. _missing_info_filters:

Missing Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As described on the :doc:`../events/index` page, sometimes an Event is missing
information. Erring on the side of caution, a Filter will skip a restriction if
the information needed to check it is missing. If your use the ``min_iv`` info,
but the IV is ``unknown`` for any reason, then by default Filter will skip
checking a restriction as if it wasn't specified.

The ``is_missing_info`` restriction can be used to require information to be
missing or not. When ``"is_missing_info":false`` is set, the Filter requires
all *checked* values to be known. When ``"is_missing_info":true`` is set, the
Filter does the opposite - at least one *checked* value must be unknown to pass.

.. warning:: The ``is_missing_info`` restriction only affects *checked*
            information. Filters only check information if a restriction
            requires it. For example, IV is only checked if either ``min_iv``
            or ``max_iv`` is set. The same is true for other values.

.. _geofences_filters:

Geofences
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For more information on configuring your ``geofence.txt``, see the :doc:`../geofences` page.

You can require an Event to be inside specific geofences for a Filter.

This example will check if an event is inside either ``"fence1"`` or ``"fence2"``
as defined in:

.. code-block:: json

  "filter_name_1":{
      "geofences":["fence1","fence2"]
  }


Geofences are checked in order. The first geofence with the event inside
will be used to define the ``<geofence>`` DTS.

If no geofences are set, the ``<geofence>`` DTS will always return ``unknown``.

If a geofence with the set name does not exist, it will be skipped and an
error will print out to the console.

Another example would be to configure alerts inside all of your geofences. You
just have to configure the geofences like this:

.. code-block:: json

  "filter_name_1":{
      "geofences":["all"]
  }

.. _custom_dts_filters:

Custom DTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Custom DTS** is a feature that allows you to specify *filter specific* DTS to
an Event when it passes a filter. The ``custom_dts`` is a JSON object of
key-value pairs. For example, the ``<family>`` DTS would be either
"Grass starters" or "Fire starters" depending on the Filter it passed with the
following configuration:

.. warning:: Using ``custom_dts`` at a Filter level will override any custom
            dts from "defaults" level - not just the specific DTS used.

.. code-block:: json

      "filters":{
          "filter_name_1":{
              "monsters":[1,2,3],
              "custom_dts":{"family":"Grass starters"}
          },
          "filter_name_2":{
              "monsters":[4,5,6],
              "custom_dts":{"family":"Fire starters"}
          }
      }
