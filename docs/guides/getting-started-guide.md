# Getting Started

## Overview

This guide contains an overview to the different parts of configuring
and customizing PokeAlarm to fit your needs.

* [Prerequisites](#prerequisites)
* [Goals](#goals)
* [Setting up an Alarm](#setting-up-an-alarm)
* [Setting up Filters](#setting-up-filters)
  * [Monster Filters](#monster-filters)
  * [Gym Filters](#gym-filters)
  * [Raid Filters](#raid-filters)
* [Customizing Alert Text](#customizing-alert-text)
* [Advanced: Managers](#advanced-managers)
* [Advanced: Missing Info](#advanced-missing-info)
* [Advanced: Custom DTS](#advanced-custom-dts)

## Prerequisites

This guide assumes the following:

1. You have correctly [installed PokeAlarm](../getting-started/installation.html),
including setting up a source for your information.

2. You are using Notepad++, Nano, or Vi(m) to configure any files. Do
**NOT** use or open any files with Notepad or TextEdit - they will
break your files!

## Goals

This guide will walk you through setting up and customizing PokeAlarm
to fit your needs. Specifically, we will go through setting up a PA
server to do the following:

1. Use Discord
2. Alert when Charmander family monsters are found.
3. Customize alerts for the other two starters based on IVs
4. Alert when an Instinct Gym falls (clearly the superior team)
5. Alert when a Raid appears for Legendary Birds
6. Customize the Monster and Raid Alerts text with DTS

## Setting up an Alarm

In PokeAlarm, an 'Alarm' is a block in the `alarms.json` section that
represents how you want to receive an alert. For our example, we will
use Discord, but the steps are similar between types of Alarms.

To create a Discord Alarm, you should be familiar with these two pages:
1. Learn how to configure your alarms file with the [Alarms](../configuration/alarms)
wiki page.
2. Learn how to set up a Discord webhook url with the [Discord](../configuration/alarms/discord.html)
wiki page.

Once we have our webhook url set up, we can edit the default discord
alarm in the `alarms.json` file:  

```json
{
  "discord_alarm":{
    "active":true,
    "type":"discord",
    "webhook_url":"https://discordapp.com/api/webhooks/1234567890"
  }
}
```
**Note**: for brevity only the discord section is shown

Try starting PokeAlarm - If you have configured your Alarm correctly,
you should see a start up message posted in your discord channel!

## Setting up Filters

Filters are how PokeAlarm decides which Events get sent to sent to the
Alarms to trigger notifications. To get all the details of Filters,
read the [Filters](../configuration/filters) wiki page.

In PokeAlarm, there are five different types of events. In a filter's
config file, there is a section for setting filters in each type of
event: `monsters`, `stops`, `gyms`, `eggs`, and `raids`.

PokeAlarm will compare each Event to each Filter, one by one. If an
Event passes a Filter, it will be passed onto the Alarms to trigger a
notification. **Note:** Only one filter can be trigger at a time.

### Monster Filters

First, we want to decide which monsters we want notifications on. I want
to create an army of Charizards, so I'm going to need a lot of candy!
I'm going to create a new filter named `best_monsters` and set it
to accept only the Charmander family:

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "best_monsters":{
                "monsters":["Charmander","Charmeleon","Charizard"]
              }
          }
  }
}
```
**Note**: for brevity only part of the filters file is shown

Bam! That was easy! So easy, maybe we should get a few of the other
starters as well. However let's only get the other starters with high
IVs (only the best IV's can compete with a monster as good as
Charmander!). Let's add another filter, but for IV's above 90%.

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "best_monsters":{
                "monsters":["Charmander","Charmeleon","Charizard"]
              },
              "okay_monsters":{
                "monsters":["Bulbasaur", 2, 3, 7, 8, 9],
                "min_iv": 90
              }
          }
  }
}
```

Wew! I got tired of typing out the names, so I just substituted
in their ID numbers instead (and PA is A-OKAY with that). I could have
also added in `"max_iv": 100` as well, but it is always better to leave
out unnecessary parameters (not only is it faster, but it can help avoid
unintended things from happening!).

### Gym Filters

Next, I want need to know when any of my team's gyms switch to another
team (so I can go put them back up). I'll start with setting
`"old_teams":["Instinct"]`.

```json
{
  "gyms":{
      "enabled":true,
      "ignore_neutral":true,
      "defaults":{
      },
      "filters":{
          "clearly_the_best_team":{
              "old_teams":["Instinct"]
          }
      }
  },
}
```
**Note**: for brevity only part of the filters file is shown

This filter will allow in any gym that switches from Instinct
to any other team. Additionally, we don't want to know about when it
switches to neutral, so we set `"ignore_neutral":true`. You can list
multiple different filters in the filters section of gyms, and PA will
check them one by one.


### Raid Filters

Raid filters work very similar to Monster Filters. You can set up alerts
for any monster - not just the ones in the example. Here is the Raid
section of a filters file set up for legendary birds:

```json
{
  "raids":{
      "enabled":true,
      "defaults":{
      },
      "filters":{
          "legendary-birds":{
              "monsters":[144, 145, 146, 249, 250]
          }
      }
  }
}
```
**Note**: for brevity only part of the filters file is shown

## Customizing Alert Text

PokeAlarm allows you to customize the Alerts that it sends out. We want
to customize our Raid Alerts to show a more appropriate message. To add
custom text to a Discord Alarm, you should be familiar with three pages:
1. Learn how to configure your alarms file with the [Alarms](../configuration/alarms)
wiki page.
2. Learn what fields Discord has to change with [Discord](../configuration/alarms/discord.html)
wiki page.
3. Learn what DTS options are available to you with the
[Events](../configuration/events) wiki page.

```json
{
  "discord_alarm":{
    "active":true,
    "type":"discord",
    "webhook_url":"https://discordapp.com/api/webhooks/1234567890",
    "raids":{
      "title":"The Legendary Bird <mon_name> has appeared! It has <cp> CP!"
    }
  }
}
```
**Note**: for brevity only part of the alarms file is shown

Dynamic Text Substitutions substitute text dynamically (shocking!). This
means that certain words will automatically change when surrounded by
`<` and `>` If a Moltres were to appear, it will show up with the
message set to `"The Legendary Bird Moltres has appeared! It has 9999
CP!"`.

**Note:** If PA doesn't have that information, it will show either '?',
'unkn', or 'unknown' instead. If you get these in your alert, you will
need to tweak your scanners to send the correct information.

You can customize any notification by adding the proper alert settings
to your alarms file. If we wanted to customize pokemon alerts, we use
the following:

```json
{
  "discord_alarm":{
    "active":true,
    "type":"discord",
    "webhook_url":"https://discordapp.com/api/webhooks/1234567890",
    "monsters":{
      "title":"The starter <mon_name> jumped out of the bushes!",
      "body":"It has an IV of <iv>%!"
    },
    "raids":{
      "title":"The Legendary Bird <mon_name> has appeared! It has <cp> CP!"
    }
  }
}
```
**Note**: for brevity only part of the alarms file is shown

You can customize more than just the title - each service has many
different options. Check out the wiki page for your specific service
for a full list.

## Advanced: Managers

Now that we've customized our message, we have a little problem. If we
add on additional filters (say for Dratini), they will have use the
message `"The starter <mon_name> jumped out of the bushes!"` But Dratini
isn't a starter pokemon! Let's add a second manager that allow us to
customize even more.

You can find out more about Manager's and their settings on the
[Managers](../configuration/managers.html) wiki page.

First, lets make two different filter files. We will call the following
filter file `starters_filter.json`:

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "best_monsters":{
                "monsters":["Charmander","Charmeleon","Charizard"]
              },
              "okay_monsters":{
                "monsters":["Bulbasaur", 2, 3, 7, 8, 9],
                "min_iv": 90
              }
          }
  }
}
```
**Note**: for brevity only part of the filters file is shown

Next, we can make a second filter file for Dratini. We will call this
one `dratini_filters.json`:

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "filter-name":{
                  "monsters":[147, 148, 149]
              }
          }
  }
}
```
**Note**: for brevity only part of the filters file is shown

We want the alerts from `starter_filters.json` to be different than the
ones from `dragon_filters.json`. So we need two different alarms files.
Here is what our `starter_alarms.json` file looks like:

```json
{
  "discord_alarm":{
    "active":true,
    "type":"discord",
    "webhook_url":"https://discordapp.com/api/webhooks/1234567890",
    "monsters":{
      "title":"The starter <mon_name> jumped out of the bushes!",
      "body":"It has an IV of <iv>%!"
    }
  }
}
```

As you can see, it is the same one as before. Here is what the
`dratini_alarms.json` file looks like:

```json
{
  "discord_alarm":{
    "active":true,
    "type":"discord",
    "webhook_url":"https://discordapp.com/api/webhooks/1234567890",
    "monsters":{
      "title":"The high IV dragon <mon_name> appears with a roar!",
      "body":"It has an IV of <iv>%!"
    }
  }
}
```

Now we have two different filters and two different alarm files.
Now we just need to set up the manager and link the filter to the alarm
we want to use. When we start PokeAlarm, we can use the following:
```
python start_pokealarm.py -m 2 -f starter_filters.json -a starter_alarms.json -f dratini_filters.json -a dragon_filters.json
```

The `-m` flag tells PA that we want 2 managers. The first manager uses
the first file specified by `-f` and the first file specified by `-a`.
The second manager uses the second filter and second alarm file.

Managers run in  separate processes, so they run concurrently and
scale well with the number of cores on your machine. However running
too many managers can be inefficient and waste your computers resources.

> *With great power comes great responsibility.*
>
> \- **Uncle Ben**  (about Managers, *probably*)

Managers are a great tool that allow you to mix and match almost every
setting to any filter or alarm settings. For full details on the power
of Managers, don't forget to check out [Managers](../configuration/managers.html)
wiki page.

## Advanced: Missing Info

Sometimes, Event's are missing information needed to correctly filter
them. In these instances, you can use the `"is_missing_info"` parameter
to require a filter to reject or allow Events with missing information.
You can read more about the feature on the
[Filters](../configuration/filters) wiki page.

I really only want monsters like Bulbasaur and Squirtle to trigger
notifications if they have the right ivs that I am looking for. If my
scanner goofs up and doesn't get the ivs, I don't want to be bothered.
Setting `"is_missing_info":false` tells that filter to reject if
any necessary information is missing.

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "best_monsters":{
                "monsters":["Charmander","Charmeleon","Charizard"]
              },
              "okay_monsters":{
                "monsters":["Bulbasaur", 2, 3, 7, 8, 9],
                "min_iv": 90, "is_missing_info":false
              }
          }
  }
}
```

## Advanced: Custom DTS

Custom DTS is a feature that let's you define filter-specific DTS that
ONLY work when that filter passes. You can read more about it on the
[Filters](../configuration/filters) wiki page.

I can use it to change certain text depending on which filters pass.

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "best_monsters":{
                "monsters":["Charmander","Charmeleon","Charizard"],
                "custom_dts":{"is_fav": "IS"}
              },
              "okay_monsters":{
                "monsters":["Bulbasaur", 2, 3, 7, 8, 9],
                "min_iv": 90, "is_missing_info":false,
                "custom_dts":{"is_fav": "IS NOT"}
              }
          }
  }
}
```

If I used the following phrase in an `alarms.json`:

`"<mon_name> <is_fav> my FAVORITE!"`

could look like this if it passed the first filter:

`Charmander IS my FAVORITE!`

or like this if it passed the second filter:

`Squirtle IS NOT my FAVORITE!`

This feature, could be used for a variety of things like tagging special
roles or even changing channels based on the filter selected.

For example, say I changed my mind and DO want notifications from the
other starters, but I want them to go into a different channel. First,
I would modify my `filters.json` to add in a DTS:

```json
{
  "monsters":{
          "enabled":true,
          "defaults":{
          },
          "filters":{
              "best_monsters":{
                "monsters":["Charmander","Charmeleon","Charizard"],
                "custom_dts":{"channel_api_key": "11111"}
              },
              "okay_monsters":{
                "monsters":["Bulbasaur", 2, 3, 7, 8, 9],
                "min_iv": 90, "is_missing_info":false,
                "custom_dts":{"channel_api_key":"11111"}
              },
              "okay_monsters_no_iv":{
                "monsters":["Bulbasaur", 2, 3, 7, 8, 9],
                "min_iv": 90, "is_missing_info":true,
                "custom_dts":{"channel_api_key":"22222"}
              }
          }
  }
}
```

Next, I can change my `alarms.json`:

```json
{
  "discord_alarm":{
    "active":true,
    "type":"discord",
    "webhook_url":"https://discordapp.com/api/webhooks/<channel_api_key>"
  }
}
```

Now, if it passes "best_monsters" or "okay_monsters" it'll send to the
channel at `https://discordapp.com/api/webhooks/11111`. If it passes
"okay_monsters_no_iv" then it will be sent to the channel at
`https://discordapp.com/api/webhooks/22222`.
