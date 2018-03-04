Discord
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:

.. role:: boltitalic
  :class: boltitalic

.. role:: underline
  :class: underline

.. role:: underlinebold
  :class: underlinebold

.. role:: underlineitalic
  :class: underlineitalic

.. role:: underlineboita
  :class: underlineboita

.. role:: strike
  :class: strike


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

**Discord** is a free voice and text chat app designed specifically for gaming.
Available on Windows, Mac OS X, iOS and Android. It is also usable from any
Chrome, Firefox or Opera browser.

PokeAlarm offers the following for Discord:

+ Custom username for posting
+ High resolution icons for pokemon, gym, pokestop, egg or raid notifications
+ Personalized notifications via :doc:`../events/index`


Basic Config
-------------------------------------


Required Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The parameters below are required to enable the Discord alarm service:

=============== ========================================
Parameters      Description
=============== ========================================
`type`          Must be ``"discord"``
`active`        ``true`` for alarm to be active
`webhook_url` * Your Webhook URL for a specific channel
=============== ========================================

.. note:: \*In PokeAlarm version 3.1, `webhook_url` replaced `api_key`.


Example: Basic Alarm Configuration using Required Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
  The above below is to be inserted into the alarms section of
  `alarms.json`. It does not represent the entire `alarms.json` file.

.. code-block:: json

  {
  	"active":true,
  	"type":"discord",
  	"webhook_url":"YOUR_WEBHOOK_URL"
  }


Advanced Config
-------------------------------------

Optional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the required parameters, several optional parameters are
available to personalize your notifications. Below is an example of these
optional parameters and how they are incorporated into a functional alarm layout.

These optional parameters are entered at the same level as ``"type":"discord"``.

+-------------------+-----------------------------------------------+----------+
| Parameters        | Description                                   | Default  |
+-------------------+-----------------------------------------------+----------+
| `startup_message` | Confirmation post when PokeAlarm initialized  | ``true`` |
+-------------------+-----------------------------------------------+----------+

These optional parameters below are applicable to the ``monsters``, ``stops``,
``gyms``, ``eggs``, and ``raids`` sections of the JSON file.

=============== ================================================ ==========================================
Parameters      Description                                      Default
=============== ================================================ ==========================================
`webhook_url`   URL of specific channel name. Overrides
                `webhook_url` at Alarm level. Use to post only
`disable_embed` Disables the body to make one line notifications ``false``
`username`      Username the bot should post the message as      ``<mon_name>``
`icon_url`      URL path to icon
`avatar_url`    URL path to avatar
`title`         Notification text to begin the message           ``A wild <mon_name> has appeared!``
`url`           Link to be added to notification text            ``<gmaps>``
`body`          Additional text to be added to the message       ``Available until <24h_time>(<time_left>).``
`content`       Text before the Discord embed
=============== ================================================ ===========================================

.. note::
  Nidorans will be ``nidoranf`` or ``nidoranm``, Farfetch'd will be
  ``farfetchd``, and Mr. Mime will be ``mrmime``.


Example: Alarm Configuration Using Optional Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
  The code below is to be inserted into the alarms section of
  ``alarms.json``. It does not represent the entire ``alarms.json`` file.

.. code-block:: json

  {
    "discord_alarm":{
      "active":true,
      "type":"discord",
      "webhook_url":"YOUR_WEBHOOK_URL",
      "startup_message":false,
      "monsters":{
          "webhook_url":"YOUR_WEBHOOK_URL_FOR_POKEMON_CHANNEL",
          "username":"<mon_name>",
          "icon_url*":"<YOUR CUSTOM URL HERE>/<mon_id_3>_<form_id_3>.png",
          "title":"A wild <mon_name> has appeared!",
          "url":"<gmaps>",
          "body":"Available until <24h_time> (<time_left>)."
      },
      "stops":{
          "webhook_url":"YOUR_WEBHOOK_URL_FOR_POKESTOP_CHANNEL",
          "username":"Pokestop",
          "icon_url*":"<YOUR CUSTOM URL HERE>/ready.png",
          "title":"Someone has placed a lure on a Pokestop!",
          "url":"<gmaps>",
          "body":"Lure will expire at <24h_time> (<time_left>)."
      },
      "gyms":{
          "webhook_url":"YOUR_WEBHOOK_URL_FOR_GYM_CHANNEL",
          "username":"<new_team> Gym Alerts",
          "icon_url*":"<YOUR CUSTOM URL HERE>/<new_team_id>.png",
          "title":"A Team <old_team> gym has fallen!",
          "url":"<gmaps>",
          "body":"It is now controlled by <new_team>."
      },
      "eggs":{
          "webhook_url":"DISCORD_WEBHOOK_URL_FOR_EGG_CHANNEL",
          "username":"Egg",
          "icon_url*":"<YOUR CUSTOM URL HERE>/<egg_lvl>.png",
          "avatar_url*":"<YOUR CUSTOM URL HERE>/<egg_lvl>.png",
          "title":"Raid is incoming!",
          "url":"<gmaps>",
          "body":"A level <egg_lvl> raid will hatch at <24h_hatch_time> (<hatch_time_left>)."
      },
      "raids":{
          "webhook_url":"DISCORD_WEBHOOK_URL_FOR_RAID_CHANNEL",
          "username":"Raid",
          "icon_url*":"<YOUR CUSTOM URL HERE>/<mon_id_3>_000.png",
          "avatar_url*":"<YOUR CUSTOM URL HERE>/<mon_id_3>_000.png",
          "title":"Level <raid_lvl> Raid is available against <mon_name>!",
          "url":"<gmaps>",
          "body":"The raid is available until <24h_raid_end> (<raid_time_left>)."
      }
    }
  }

.. note::
  \*THESE LINES ARE USED TO OVERRIDE DEFAULT VALUES. IF YOU DO NOT WISH
  TO USE CUSTOM IMAGES, DO NOT ADD THESE LINES TO YOUR ALARMS.JSON.

Mini Map Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. image:: ../../images/minimap.png

You can enable a small Google Static Maps image after your post, showing the
location of the alarmed pokemon, gym, pokestop, egg, or raid. This is done by
adding the ``map`` parameter at the Alarm level (which will apply maps for any
notification), or individually to the ``monsters``, ``stops``, ``gyms``,
``eggs``, or ``raids`` sections of your alarm.

Below is an example of enabling the mini map for pokemon.

.. code-block:: json

	"monsters":{
		"webhook_url":"YOUR_WEBHOOK_URL_FOR_POKEMON_CHANNEL",
		"username":"<mon_name>",
		"title":"A wild <mon_name> has appeared!",
		"url":"<gmaps>",
		"body":"Available until <24h_time> (<time_left>).",
		"map":{
			"enabled":true,
			"width":"250",
			"height":"125",
			"maptype":"roadmap",
			"zoom":"15"
		}
	},


=========== ====================================== =============
Parameters  Description                            Default
=========== ====================================== =============
`enabled`   Turns the map on or off                ``true``
`width`     Width of the map                       ``"250"`` px
`height`    Height of the map                      ``"150"`` px
`maptype`   Link to be added to notification text  ``"roadmap"``
`zoom`      Specifies the zoom of the map          ``"15"``
=========== ====================================== =============


Formatting alarms text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a basic guide to apply custom styles to alarm text:

=================================== ========================================
Style                               Example
=================================== ========================================
`*italics*`                         *italics*
`**bold**`                          **bold**
`***bold italics***`                :boltitalic:`bold italics`
`__underline__`                     :underline:`underline`
`__*underline italics*__`           :underlineitalic:`underline italics`
`__**underline bold**__`            :underlinebold:`underline bold`
`__***underline bold italics***__`  :underlineboita:`underline bold italics`
`~~strikethrough~~`                 :strike:`strikethrough`
=================================== ========================================

You can see other options in the official Discord information about
formatting text `here <https://support.discordapp.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline->`_.


How to enable Discord webhooks
-------------------------------------

1. You must have the role permission ``Manage Webhooks``, or be an administrator
   for the server.

2. Go into channel settings, into the Webhooks tab.

3. Click ``Create Webhook``, ``Save``

4. The webhook URL listed is the key you need.
