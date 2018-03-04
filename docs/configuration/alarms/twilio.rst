Twilio
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:


Prerequisites
-------------------------------------

This guide assumes

+ You are familiar with `JSON formatting <https://www.w3schools.com/js/js_json_intro.asp>`_.
+ You have read and understood the :doc:`index` wiki.
+ You are comfortable with the layout of ``alarms.json``.
+ You are using the latest version of PokeAlarm.

Please familiarize yourself with all of the above before proceeding.


Introduction
-------------------------------------

**Twilio** allows software developers to programmatically make and receive
phone calls and send and receive text messages using its web service APIs.

PokeAlarm offers the following for Twilio:

+ Personalized notifications via :doc:`../events/index`


Basic Config
-------------------------------------

These ``alarms.json`` parameters are required to enable the alarm service:


Required Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

=============== ======================================
Parameters      Description
=============== ======================================
`type`          Must be ``"twilio"``
`active`        ``true`` for alarm to be active
`account_sid`   Your Account SID from Twilio
`auth_token`    Your Auth Token from Twilio
`from_number`   Your Twilio number to send from
`to_number`     Your number to receive texts from
=============== ======================================


Example: Basic Alarm Configuration using Required Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

  {
  	"active":true,
  	"type":"twilio",
  	"account_sid":"YOUR_API_KEY",
  	"auth_token":"YOUR_AUTH_TOKEN",
  	"from_number":"YOUR_FROM_NUM",
  	"to_number":"YOUR_TO_NUM"
  }

.. note::
  The above code is to be inserted into the alarms section of
  alarms.json. It does not represent the entire alarms.json file.


Advanced Config
-------------------------------------

In addition to the above required parameters, several optional parameters
are available to personalize your notifications.


Multiple Destinations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``"to_number"`` field can accept either a single destination phone number
or an array of phone numbers to send SMS messages to. This allows for
sending SMS alerts to multiple destinations.

Below is an example of using an array for the destination number(s) in the
alarm configuration.

.. code-block:: json

  {
  	"active":true,
  	"type":"twilio",
  	"account_sid":"YOUR_API_KEY",
  	"auth_token":"YOUR_AUTH_TOKEN",
  	"from_number":"YOUR_FROM_NUM",
  	"to_number":["YOUR_1ST_TO_NUM","YOUR_2ND_TO_NUM","YOUR_3RD_TO_NUM"]
  }


Optional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These optional parameters below are applicable to the ``monsters``, ``stops``,
``gyms``, ``eggs``, and ``raids`` sections of the JSON file.

``monsters`` default values:

=========== ================================= ===================================
Parameters  Description                       Default
=========== ================================= ===================================
`message`   Text message for pokemon updates  ``"A wild <mon_name> has appeared!
                                              <gmaps> Available until <24h_time>
                                              (<time_left>)."``
=========== ================================= ===================================

``stops`` default values:

=========== ================================= ===================================
Parameters  Description                       Default
=========== ================================= ===================================
`message`   Text message for pokestop updates ``"Someone has placed a lure on a
                                              Pokestop! <gmaps> Lure will expire
                                              at <24h_time> (<time_left>)."``
=========== ================================= ===================================

``gyms`` default values:

=========== ================================= ===================================
Parameters  Description                       Default
=========== ================================= ===================================
`message`   Text message for gym updates      ``"A Team <old_team> gym has fallen!
                                              <gmaps> It is now controlled by
                                              <new_team>."``
=========== ================================= ===================================

``eggs`` default values:

=========== ================================= =====================================
Parameters  Description                       Default
=========== ================================= =====================================
`message`   Text message for egg updates      ``"A level <egg_lvl> raid is incoming!
                                              <gmaps> Egg hatches <24h_hatch_time>
                                              (<hatch_time_left>)."``
=========== ================================= =====================================

``raids`` default values:

=========== ================================= =====================================
Parameters  Description                       Default
=========== ================================= =====================================
`message`   Text message for raid updates     ``"Level <raid_lvl> raid against
                                              <mon_name>! <gmaps> Available until
                                              <24h_raid_end> (<raid_time_left>)."``
=========== ================================= =====================================


Example: Alarm Configuration Using Optional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below is an example of these optional parameters and how they are incorporated
into a functional alarm layout.

.. code-block:: json

  {
    "twilio_alarm":{
      "active":true,
      "type":"twilio",
      "account_sid":"YOUR_API_KEY",
      "auth_token":"YOUR_AUTH_TOKEN",
      "from_number":"YOUR_FROM_NUM",
      "to_number":"YOUR_TO_NUM",
      "monsters":{
          "from_number":"YOUR_FROM_NUM",
          "to_number":"YOUR_TO_NUM",
          "message":"A wild <mon_name> has appeared! <gmaps> Available until <24h_time> (<time_left>)."
      },
      "stops":{
          "from_number":"YOUR_FROM_NUM",
          "to_number":"YOUR_TO_NUM",
          "message":"Someone has placed a lure on a Pokestop! <gmaps> Lure will expire at <24h_time> (<time_left>)."
      },
      "gyms":{
          "from_number":"YOUR_FROM_NUM",
          "to_number":"YOUR_TO_NUM",
          "message":"A Team <old_team> gym has fallen! <gmaps> It is now controlled by <new_team>."
      },
      "eggs":{
          "message":"A level <egg_lvl> raid is incoming! <gmaps> Egg hatches <24h_hatch_time> (<hatch_time_left>)."
      },
      "raids":{
         "message":"Level <raid_lvl> raid against <mon_name>! <gmaps> Available until <24h_raid_end> (<raid_time_left>)."
      }
    }
  }


.. note::
  The above code is to be inserted into the alarms section of
  alarms.json. It does not represent the entire alarms.json file.


How to get the Account SID, Auth Token, and Twilio Number
-------------------------------------

1. Go to `Twilio <https://www.twilio.com>`_ and click ``Get a free API key``.
   Fill out the following form, and enter your phone number to verify your
   account.

2. On the left hand side, click the Home Button and then click Dashboard.
   The **Account SID** and **Auth Token** will be listed. To reveal the Auth
   Token, click on the lock next to it.

3. Scroll down and click on ``# Phone Numbers``. Then click ``Get Started``
   to get your free number.

4. If you wish to text to different numbers, you need to register each before
   you are allowed to message them. This can be done from the ``Verified Caller
   ID's`` page.
