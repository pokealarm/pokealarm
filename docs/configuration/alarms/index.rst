Alarms
=======

.. contents:: Table of Contents
   :depth: 2
   :local:

Prerequisites
-------------------------------------

This pages assumes the following:

+ You understand how :doc:`../events/index` and :doc:`../filters/index` work.
+ You understand what :ref:`DTS <events_dts>` are.
+ You understand
  `JSON formatting <https://www.w3schools.com/js/js_json_intro.asp>`_.
+ You are using the latest version of PokeAlarm.


Introduction
-------------------------------------

An **Alarm** object describes where and how PA is going to send a notification
once it has been properly triggered. When an Event passes a Filter, it is next
sent to the Alarms. Each Alarm represents settings for exactly a notification to
be sent: which service, what text,  what images, and more.

.. note:: By default, PA will trigger every Alarm when an Event passes a Filter.
          You can override this behavior by using the advanced
          :doc:`../Rules-Overview` feature.

There are several different types of Alarms, each representing a different
service:

.. toctree::
   :maxdepth: 1
   :glob:

   *

.. note:: It is totally valid to have multiple Alarms with the same type - a
          different Alarm could represent a different channel or a specialized
          message instead of just a different service.


In PokeAlarm, an "Alarm" is defined as a supported message service that sends
a notification. Slack, Twitter, Telegram, each are considered message service.

PokeAlarm allows you to add as many different supported message services as
you'd like (e.g., Slack, Twitter, Telegram), and as many of each message
service that you would like (e.g., 3 Slack channels, 10 Twitter feeds, 5 Telegrams.)

You add alarms to the PokeAlarm alarm configuration file, which is `alarms.json` by default.

`alarms.json` is where:

1. Alarms are enable/disabled
2. Notification messages for each alarm are customized

The alarm configuration file follows the JSON format and has six sections:

1. `alarms`
2. `monsters`
3. `stops`
4. `gyms`
5. `eggs`
6. `raids`

### Editing or Adding Alarms

To add, edit, or remove alarms, edit the `alarms.json` file. If you haven't
created an `alarms.json` file before, you can make a copy of
`alarms.json.example` and rename it to `alarms.json`. PokeAlarm uses
`alarms.json` by default.

Alarms are represented as a list of JSON Objects, inside an array labeled
alarms. Each alarm should be surrounded by curly brackets, and the space in
between fields should have a comma. Your default `alarms.json` looks like this:

.. code-block:: json
  {
    "discord_alarm":{
      "active":false,
      "type":"discord",
      "webhook_url":"YOUR_WEBHOOK_URL"
    },
    "facebook_alarm":{
      "active":false,
      "type":"facebook_page",
      "page_access_token":"YOUR_PAGE_ACCESS_TOKEN"
    },
    "pushbullet_alarm":{
      "active":false,
      "type":"pushbullet",
      "api_key":"YOUR_API_KEY"
    },
    "slack_alarm":{
      "active":false,
      "channel":"general",
      "type":"slack",
      "api_key":"YOUR_API_KEY"
    },
    "telegram_alarm":{
      "active":false,
      "type":"telegram",
      "bot_token":"YOUR_BOT_TOKEN",
      "chat_id":"YOUR_CHAT_ID"
    },
    "twilio_alarm":{
      "active":false,
      "type":"twilio",
      "account_sid":"YOUR_API_KEY",
      "auth_token":"YOUR_AUTH_TOKEN",
      "from_number":"YOUR_FROM_NUM",
      "to_number":"YOUR_TO_NUM"
    },
    "twitter_alarm":{
      "active":false,
      "type":"twitter",
      "access_token":"YOUR_ACCESS_TOKEN",
      "access_secret":"YOUR_ACCESS_SECRET",
      "consumer_key":"YOUR_CONSUMER_KEY",
      "consumer_secret":"YOUR_CONSUMER_SECRET"
    }
  }

Each alarm requires some sort of API key or URL so that PokeAlarm can gain
permissions to post.  Visit the wiki page of the service you are setting up to
make sure you have the proper config.

Each alarm setting runs independent of the other alarms, so changes to one
alarm do not affect the others (even if they are of the same type).

If is perfectly valid to have any combination of services, including repeats.

### Customizing Alerts

Most alarms have customizable fields for each alert that allow you to insert
your own message. This allows your to override the standard message and provide
your own. You may customize as few or as many fields as you want - any field
not present in your config will reset to default.

In order to customize an Alert, you must specify what type of alert you want to
config: Either `monsters`, `stops`, `gyms`, `eggs`, or `raids`. Each of these
has different defaults available. The following is a config where a portion of
the Alert has been updated:

```json
{
  "slack_alarm":{
    "active":true,
    "type":"slack",
    "api_key":"YOUR_API_KEY_HERE",
    "monsters":{
      "channel":"Pokemon",
		  "username":"<mon_name>",
		  "title":"A GIANT <mon_name> jumped out of the grass!",
		  "body":"Available until <24h_time> (<time_left>)."
    },
    "stops":{
		  "channel":"Pokestop",
		  "title":"Someone  has placed a lure on a Pokestop!",
		  "body":"Better hurry! The lure only has <time_left> remaining!"
    }
  }
}
```

For more information about Dynamic Text Substitutions (the `<text>`), please
see the Dynamic Text Substitution wiki.

For what service has what fields, please check the specific wiki page for
that service.

### Example `alarms.json`

Below is a working alarm configuration for Discord and Slack:

```json
{
    "discord_alarm":{
        "active":true,
        "type":"discord",
        "webhook_url":"DISCORD_WEBHOOK_URL_FOR_FALLBACK",
        "startup_message":false,
        "monsters":{
            "webhook_url":"DISCORD_WEBHOOK_URL_FOR_POKEMON_CHANNEL",
            "username":"<mon_name>",
            "title":"<mon_name> **<cp>CP** (**<iv>% <atk>/<def>/<sta>**, <quick_move>/<charge_move>) at <address> <postal>",
            "url":"<gmaps>",
            "body":"Available until <24h_time> (<time_left> remaining)"
        },
        "stops":{
            "username":"Pokestop",
            "webhook_url":"DISCORD_WEBHOOK_URL_FOR_POKESTOP_CHANNEL",
            "title":"[<neighborhood>] <address> <postal>",
            "url":"<gmaps>",
            "body":"expires at <24h_time> (<time_left>)."
        },
        "gyms":{
            "webhook_url":"DISCORD_WEBHOOK_URL_FOR_GYM_CHANNEL",
            "username":"<new_team> Gym Alerts",
            "title":"[<neighborhood>] <address> <postal>",
            "url":"<gmaps>",
            "body":"A team <old_team> gym has fallen to <new_team>."
        },
        "eggs":{
            "webhook_url":"DISCORD_WEBHOOK_URL_FOR_EGG_CHANNEL",
            "username":"Egg",
            "title":"Raid is incoming!",
            "url":"<gmaps>",
            "body":"A level <egg_lvl> raid will hatch at <24h_hatch_time> (<hatch_time_left>)."
        },
        "raids":{
            "webhook_url":"DISCORD_WEBHOOK_URL_FOR_RAID_CHANNEL",
            "username":"<mon_name> Raid",
            "title":"Level <raid_lvl> raid is available against <mon_name>!",
            "url":"<gmaps>",
            "body":"The raid is available until <24h_raid_end> (<raid_time_left>)."
        }
    },
    "slack_alarm":{
        "active":true,
        "type":"slack",
        "api_key":"YOUR_SLACK_API_KEY",
        "startup_message":false,
        "monsters":{
            "channel":"pokemon",
            "username":"<mon_name>",
            "title":"*<mon_name>* (<iv>% <atk>/<def>/<sta>) in <neighborhood> at <address> <postal>",
            "url":"<gmaps>",
            "body":"Available until <24h_time> (<time_left>)\n*Moves:* <quick_move> / <charge_move>",
            "map":{
                "enabled":true,
                "width":"330",
                "height":"250",
                "maptype":"roadmap",
                "zoom":"17"
            }
        },
        "stops":{
            "channel":"pokestops",
            "username":"Pokestop",
            "title":"[<neighborhood>] <address> <postal>",
            "url":"<gmaps>",
            "body":"expires at <24h_time> (<time_left>).",
            "map":{
                "enabled":false,
                "width":"330",
                "height":"250",
                "maptype":"roadmap",
                "zoom":"15"
            }
        },
        "gyms":{
            "channel":"gyms",
            "username":"<new_team> Gym Alerts",
            "title":"[<neighborhood>] <address> <postal>",
            "url":"<gmaps>",
            "body":"A team <old_team> gym has fallen to <new_team>.",
            "map":{
                "enabled":true,
                "width":"330",
                "height":"250",
                "maptype":"terrain",
                "zoom":"13"
            }
        }
    }
}
```

Note both have `"active":"true"` set, meaning both alarms are enabled. Setting
either to "false" will disable the specific alarm.. This allows you to have
alarms set up and ready to go, but only enabled when you want them.

Visit the wiki article on [Filters](Filters) to limit pokemon notifications
by distance, %IV, and moves with the `filters.json` file.


.. toctree::
   :titlesonly:
   :glob:

   *
