Twitter
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

**Twitter** is an online social networking service that enables users to send
and read short 140-character messages called "tweets". Registered users can
read and post tweets, but those who are unregistered can only read them. Users
access Twitter through the website interface, SMS or mobile device app.

PokeAlarm offers the following for Twitter:

+ Personalized notifications via :doc:`../events/index`

Basic Config
-------------------------------------


Required Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

These ``alarms.json`` parameters are required to enable the Twitter alarm service:

================= ==================================
Parameters        Description
================= ==================================
`type`            Must be ``"twitter"``
`active`          ``true`` for alarm to be active
`access_token`    Your twitter access token
`access_secret`   Your twitter access secret
`consumer_key`    Your twitter consumer key
`consumer_secret` Your twitter consumer secret
================= ==================================


Example: Basic Alarm Configuration using Required Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

  {
  	"active":true,
  	"type":"twitter",
  	"access_token":"YOUR_ACCESS_TOKEN",
  	"access_secret":"YOUR_ACCESS_SECRET",
  	"consumer_key":"YOUR_CONSUMER_KEY",
  	"consumer_secret":"YOUR_CONSUMER_SECRET"
  }

.. note::
  The above code is to be inserted into the alarms section of
  `alarms.json`. It does not represent the entire `alarms.json` file.


Advanced Config
-------------------------------------


Optional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the required parameters, several ``alarms.json`` optional
parameters are available to personalize your notifications. Below is an
example of these optional parameters and how they are incorporated into a
functional alarm layout.

These optional parameters are entered at the same level as ``"type":"twitter"``.

+-------------------+-----------------------------------------------+----------+
| Parameters        | Description                                   | Default  |
+-------------------+-----------------------------------------------+----------+
| `startup_message` | Confirmation post when PokeAlarm initialized  | ``true`` |
+-------------------+-----------------------------------------------+----------+

These optional parameters below are applicable to the ``monsters``, ``stops``,
``gyms``, ``eggs``, and ``raids`` sections of the JSON file.

============ ========================== ==========================================
Parameters   Description                Default
============ ========================== ==========================================
`status`     Message to post as status  ``"A wild <mon_name> has appeared!
                                        Available until <24h_time> (<time_left>).
                                        <gmaps>"``
============ ========================== ==========================================


Example: Alarm Configuration Using Optional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

  {
    "twitter_alarm":{
      "active":true,
      "type":"twitter",
      "access_token":"YOUR_ACCESS_TOKEN",
      "access_secret":"YOUR_ACCESS_SECRET",
      "consumer_key":"YOUR_CONSUMER_KEY",
      "consumer_secret":"YOUR_CONSUMER_SECRET",
      "monsters":{
          "status":"A wild <mon_name> has appeared! Available until <24h_time> (<time_left>). <gmaps>"
      },
      "stops":{
          "status":"Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>). <gmaps>"
      },
      "gyms":{
          "status":"A Team <old_team> gym has fallen! It is now controlled by <new_team>. <gmaps>"
      },
      "eggs":{
          "status":"Level <egg_lvl> raid incoming! Hatches at <24h_hatch_time> (<hatch_time_left>). <gmaps>"
      },
      "raids":{
          "status":"Raid <raid_lvl> against <mon_name>! Available until <24h_raid_end> (<raid_time_left>). <gmaps>"
      }
    }
  }


.. note::
  The above code is to be inserted into the alarms section of
  ``alarms.json``. It does not represent the entire ``alarms.json`` file.

For more information on text substitutions, please see the main configuration page.


How to get a Twitter API Key
-------------------------------------

**Step 1: Create a Twitter account**

+ Go to `Twitter's signup page <https://twitter.com/signup>`_.
+ Fill out all details, and **make sure to include your phone number**. This
  is a requirement for remote access, and you will need that to make the Twitter
  bot work.

**Step 2: Create a Twitter app**

+ Go to `apps.twitter.com <https://apps.twitter.com>`_
+ Click ``Create New App`` button
+ Fill out the details on the form. You have to give your app a name,
  description, and website. This can be a simple place holder like
  http://www.example.com
+ Read the Developer Agreement, and check the box at the bottom if you agree.
  Then click on the ``Create your Twitter application`` button.

**Step 3: Keys and Access tokens**

+ After creating your new app, you were redirected to its own page. If you
  weren’t, go to `apps.twitter.com <https://apps.twitter.com>`_ and click on
  your apps name.
+ On the app’s page, click on the ``Keys and Access Tokens`` page.
+ At the bottom of this page, click on the ‘Create my access token’ button.
+ Take note of **Consumer Key (API Key), Consumer Secret (API Secret), Access
  Token, & Access Token Secret**. These are the are required in the Twitter Config.
