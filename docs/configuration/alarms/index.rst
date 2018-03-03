Alarms
=======

.. contents:: Table of Contents
   :depth: 1
   :local:

Prerequisites
-------------------------------------

This guide assumes:

+ You understand how :doc:`../events/index` and :doc:`../filters/index` work.
+ You understand what how :ref:`DTS <events_dts>` work.
+ You understand
  `JSON formatting <https://www.w3schools.com/js/js_json_intro.asp>`_.
+ You are using the latest version of PokeAlarm.


Introduction
-------------------------------------

An **Alarm** object describes where and how PA is going to send a notification
once it has been properly triggered. When an Event passes a Filter, it is passed
on to the Alarms to trigger notifications. Each Alarm represents settings for
exactly a notification will be sent: which service, what text, what images, and
more.

.. note:: By default, PA will trigger every Alarm when an Event passes a Filter.
          You can override this behavior by using the advanced
          :doc:`../rules-overview` feature.

There are several different types of Alarms, each representing a different type
of service:

.. toctree::
   :maxdepth: 1

   discord
   facebook-pages
   pushbullet
   slack
   telegram
   twilio
   twitter


.. note:: It is valid to have multiple Alarms with the same type - a
          different Alarm could represent a different channel or a specialized
          message instead of just a different service.


Creating an Alarm
-------------------------------------

Each Alarm is containing several key-value a *named* JSON Object containing
several key-value pairs called *alarm parameters*. Some parameters are
**required** for each alarm, and some are **optional** parameters. In the case of
optional parameters, default values are generally provided when they aren't
specified. For example, a basic Discord alarm looks like this:

.. code-block:: json

    "my-discord-alarm":{
    	"active":true,
    	"type":"discord",
    	"webhook_url":"YOUR_WEBHOOK_URL"
    }

The available parameters are different for every type of Alarm - make sure to
check the appropriate wiki page to ensure you are using the correct ones.


Customizing Alerts
-------------------------------------

It is possible to customize the parameters an Alarm uses for different types of
Events. For example, you may want to send all "monsters" to one channel and all
"raids" to another. In this case, *alert level* parameters can be used. These
parameters override the *alarm level* parameters when used. Here is an example
that uses alarm using alert level parameters:

.. code-block:: json

    "my-discord-alarm":{
    	"active":true,
    	"type":"discord",
    	"webhook_url":"DEFAULT_CHANNEL_URL",
    	"monsters":{
    	  "webhook_url":"MONSTER_CHANNEL_URL"
    	},
    	"raids":{
    	  "webhook_url":"RAIDS_CHANNEL_URL"
    	}
    }


In the above example, any *alert level* parameters not set will default to the
*alarm level* parameters - this means "stops", "gyms", and "eggs" will all be
diverted to the channel at ``"DEFAULT_CHANNEL_URL"``.

Additionally, are also several *alert level* parameters that can't be set at the
alarm level. For example, "body" can **only** be set at the alert level in
Discord:

.. code-block:: json

    "my-discord-alarm":{
    	"active":true,
    	"type":"discord",
    	"webhook_url":"DEFAULT_CHANNEL_URL",
    	"monsters":{
    	  "webhook_url":"MONSTER_CHANNEL_URL",
    	  "body":"This is a monster event!"
    	},
    	"raids":{
    	  "webhook_url":"RAIDS_CHANNEL_URL",
    	  "body":"This is a raid event!"
    	}
    }


Finally, you can use :ref:`DTS <events_dts>` to customize most parameters based
on the event. This can be used for a variety of reasons: specializing the
message, customizing the channel, or even inserting your own images. Check out
:ref:`DTS <events_dts>` for information on DTS.


Alarms File
-------------------------------------

An *alarms file* (sometimes referred to as an 'alarms.json') is a file
containing then Alarms that PA uses. By default, PA loads from the
``alarms.json`` located in the base folder of the project. See the
:doc:`../server-settings` page for instructions on specifying the file by a
different name. This file must contain a single JSON object to load
successfully:

.. code-block:: json

    {

    }

Each Alarm will be listed inside this JSON object. It will end up looking
something like this:

.. code-block:: json

    {
      "my-first-alarm":{
        "active":true,
        "type":"discord",
        "webhook_url":"YOUR_WEBHOOK_URL"
      },
      "my-second-alarm":{
      	"active":true,
      	"type":"slack",
      	"api_key":"YOUR_API_KEY",
      	"channel":"general"
      },
      "my-third-alarm":{
        "active":true,
        "type":"discord",
        "webhook_url":"YOUR_WEBHOOK_URL"
      }
    }
