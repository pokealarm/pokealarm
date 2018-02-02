# Discord

## Overview

* [Prerequisites](#prerequisites)
* [Introduction](#introduction)
* [Basic Config](#basic-config)
  * [Required Parameters](#required-parameters)
  * [Example: Basic Alarm Configuration using Required Parameters](#example-basic-alarm-configuration-using-required-parameters)
* [Advanced Config](#advanced-config)
  * [Optional Parameters](#optional-parameters)
  * [Example: Alarm Configuration Using Optional Parameters](#example-alarm-configuration-using-optional-parameters)
  * [Mini Map Configuration](#mini-map-configuration)
  * [Formatting alarms text](#formatting-alarms-text)
* [How to Enable Discord Webhooks](#how-to-enable-discord-webhooks)

## Prerequisites

This guide assumes

1. You are familiar with [JSON formatting](https://www.w3schools.com/js/js_json_intro.asp)
2. You have read and understood the [Alarms](alarms) Wiki
3. You are comfortable with the layout of `alarms.json`.
4. You are using the latest version of PokeAlarm.

Please familiarize yourself with all of the above before proceeding.

## Introduction

**Discord** is a free voice and text chat app designed specifically for gaming.
Available on Windows, Mac OS X, iOS and Android. It is also usable from any
Chrome, Firefox or Opera browser.

PokeAlarm offers the following for Discord:

* Custom username for posting
* High resolution icons for pokemon, gym, pokestop, egg or raid notifications
* Personalized notifications via [Dynamic Text Substitution](Dynamic-Text-Substitution)

## Basic Config

### Required Parameters

The parameters below are required to enable the Discord alarm service:

<!--table-->
| Parameters     | Description                             |
|----------------|-----------------------------------------|
| `type`         | Must be `discord`                       |
| `active`       | `true` for alarm to be active           |
| `webhook_url`* | Your Webhook URL for a specific channel |
<!--endtable-->

**Note:** *In PokeAlarm version 3.1, `webhook_url` replaced `api_key`.*

### Example: Basic Alarm Configuration using Required Parameters

**Note:** The above below is to be inserted into the alarms section of
`alarms.json`. It does not represent the entire `alarms.json` file.

```json
{
	"active":true,
	"type":"discord",
	"webhook_url":"YOUR_WEBHOOK_URL"
}
```

## Advanced Config

### Optional Parameters

In addition to the required parameters, several optional parameters are
available to personalize your notifications. Below is an example of these
optional parameters and how they are incorporated into a functional alarm layout.

These optional parameters are entered at the same level as `"type":"discord"`.

<!--table-->
| Parameters         | Description                                  |
|--------------------|----------------------------------------------|
| `startup_message`  | Confirmation post when PokeAlarm initialized |
<!--endtable-->

These optional parameters below are applicable to the `monsters`, `stops`,
`gyms`, `eggs`, and `raids` sections of the JSON file.

<!--table-->
| Parameters       | Description                                  | Default                           |
|------------------|----------------------------------------------|-----------------------------------|
| `webhook_url`    | URL of specific channel name. Overrides `webhook_url` at Alarm level. Use to post only
| `disable_embed`  | Disables the body to make one line notifications | `False`                       |
| `username`       | Username the bot should post the message as  | `<mon_name>`                      |
| `icon_url`       | URL path to icon                             |                                   |
| `avatar_url`     | URL path to avatar                           |                                   |
| `title`          | Notification text to begin the message       | `A wild <mon_name> has appeared!` |
| `url`            | Link to be added to notification text        | `<gmaps>`                         |
| `body`           | Additional text to be added to the message   | `Available until <24h_time> (<time_left>).` |
| `content`        | Text before the Discord embed                |                                   |
<!--endtable-->

*Note: Nidorans will be `nidoranf` or `nidoranm`, Farfetch'd will be
`farfetchd`, and Mr. Mime will be `mrmime`.*

## Example: Alarm Configuration Using Optional Parameters

**Note:** The code below is to be inserted into the alarms section of
`alarms.json`. It does not represent the entire `alarms.json` file.

```json
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
```
**Note:** \*THESE LINES ARE USED TO OVERRIDE DEFAULT VALUES. IF YOU DO NOT WISH
TO USE CUSTOM IMAGES, DO NOT ADD THESE LINES TO YOUR ALARMS.JSON.

### Mini Map Configuration

![](images/minimap.png)

You can enable a small Google Static Maps image after your post, showing the
location of the alarmed pokemon, gym, pokestop, egg, or raid. This is done by
adding the `map` parameter at the Alarm level (which will apply maps for any
notification), or individually to the `monsters`, `stops`, `gyms`, `eggs`,
or `raids` sections of your alarm.

Below is an example of enabling the mini map for pokemon.

```json
	"monsters":{
		"webhook_url":"YOUR_WEBHOOK_URL_FOR_POKEMON_CHANNEL",
		"username":"<mon_name>",
		"title":"A wild <mon_name> has appeared!",
		"url":"<gmaps>",
		"body":"Available until <24h_time> (<time_left>).",
		"map":{
			"enabled":"true",
			"width":"250",
			"height":"125",
			"maptype":"roadmap",
			"zoom":"15"
		}
	},
```

<!--table-->
| Parameters     | Description                           | Default     |
|----------------|---------------------------------------|-------------|
| `enabled`      | Turns the map on or off               | `true`      |
| `width`        | Width of the map                      | `250` px    |
| `height`       | Height of the map                     | `150` px    |
| `maptype`      | Link to be added to notification text | `roadmap`   |
| `zoom`         | Specifies the zoom of the map         | `15`        |
<!--endtable-->

### Formatting alarms text

Here is a basic guide to apply custom styles to alarm text:


+------------------------------------+----------------------------------+
| Style                              | Example                          |
|====================================+==================================+
| `*italics*`                        | *italics*                        |
+------------------------------------+----------------------------------+
| `**bold**`                         | **bold**                         |
+------------------------------------+----------------------------------+
| `***bold italics***`               | ***bold italics***               |
+------------------------------------+----------------------------------+
| `__underline__`                    | __underline__                    |
+------------------------------------+----------------------------------+
| `__*underline italics*__`          | __*underline italics*__          |
+------------------------------------+----------------------------------+
| `__**underline bold**__`           | __**underline bold**__           |
+------------------------------------+----------------------------------+
| `__***underline bold italics***__` | __***underline bold italics***__ |
+------------------------------------+----------------------------------+
| `~~Strikethrough~~`                | ~~Strikethrough~~                |
+------------------------------------+----------------------------------+

You can see other options in the official Discord information about formatting text [here](https://support.discordapp.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-).

## How to enable Discord webhooks

1. You must have the role permission 'Manage Webhooks', or be an administrator for the server.

2. Go into channel settings, into the Webhooks tab.

3. Click "Create Webhook", 'Save'

4. The webhook URL listed is the key you need.
