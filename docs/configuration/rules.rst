Rules
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:

Prerequisites
-------------------------------------

This guide assumes the following:

+ You are using the latest version of PokeAlarm.
+ You understand how to configure :doc:`filters/index`.
+ You understand how to configure :doc:`alarms/index`.


Introduction
-------------------------------------

In PokeAlarm, a **Rule** is a what decides which :doc:`filters/index` are
checked before being sent to which :doc:`alarms/index`. When PA processes an
Event, each Rule is a chance for a notification to be sent. The Event is
compared against each Filter listed, until it finds a match. Once matched, it
is passed on the listed Alarms, triggering a notification for each.

If no rules are defined, PA follows the "default" rule. It checks every Filter
available, and if it finds a match it triggers every Alarm. By setting a
Rule, you can customize this behavior.

.. warning:: Rules are processed independently of each other. If an Alarm is
             listed in two different Rules that both pass, it's possible for a
             notification to trigger twice.

Custom Rules
-------------------------------------

A **Rule** is represented as *named* JSON Object with only two parameters.
``"filters"`` is a list of Filters by name, and ``"alarms"`` is a list of
Alarms by name.

.. warning:: Attempting to create a Rule with a non existent Filter or Alarm
             will throw an error - make sure your spelling is correct!

.. code-block:: json

    "rule_example": {
        "filters": ["filter_name_1", "filter_name_2", "filter_name_3"],
        "alarms": ["alarm_name_1", "alarm_name_2", "alarm_name_3"]
    }

In the above example, PA wil check ``"filter_name_1"``, followed by
``"filter_name_2"``, followed by ``"filter_name_3"``. If at any point an Event
matches a filter, it will cease checking and triggers all 3 listed Alarms.

Rules File
-------------------------------------

A *rules file* (sometimes referred to as ``rules.json``) is a file describing
the rules that PA uses. By default, PA doesn't load any rules file. See the
:doc:`../server-settings` page for instructions on specifying the file.
This file must contain a single JSON object to load successfully:

.. code-block:: json

    {

    }

Inside this JSON object, you need to add sections for each type of Filter you
wish to add. Sections are optional, and unspecified sections will use the
default rule.

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

Each section is a JSON object that can contain the rules for that section. For
example, a potential ``"monsters`` section might look like this:

.. code-block:: json

    {
      "monsters":{
        "my_first_rule": {
          "filters": ["uncommon_spawns", "okay_spawns"],
          "alarms": ["discord_okay_channel", "telegram_okay_channel"]
        },
        "my_second_rule": {
          "filters": ["100iv", "best_spawns"],
          "alarms": ["discord_best_channel", "telegram_best_channel"]
        }
      }
    }

In the above, if an Event passes either the ``"uncommon_spawns"`` or the
``"okay_spawns"`` filter, it will trigger the ``"discord_okay_channel"`` and
``"telegram_okay_channel"`` alarms. However, if it passes either the
``"100iv"`` or ``"best_spawns"`` filter, then it will trigger the
``"discord_best_channel"`` and ``"telegram_best_channel"`` alarms.
