# Twilio

## Overview

* [Prerequisites](#prerequisites)
* [Introduction](#introduction)
* [Basic Config](#basic-config)
  * [Required Parameters](#required-parameters)
  * [Example: Basic Alarm Configuration using Required Parameters](#example-basic-alarm-configuration-using-required-parameters)
* [Advanced Config](#advanced-config)
  * [Multiple Destinations](#multiple-destinations)
  * [Optional Parameters](#optional-parameters)
  * [Example: Alarm Configuration Using Optional Parameters](#example-alarm-configuration-using-optional-parameters)
* [How to get the Account SID, Auth Token, and Twilio Number](#how-to-get-the-account-sid-auth-token-and-twilio-number)

## Prerequisites

This guide assumes:

1. You are familiar with [JSON formatting](https://www.w3schools.com/js/js_json_intro.asp)
2. You have read and understood the [Alarms](alarms) Wiki
3. You are comfortable with the layout of `alarms.json`.

## Introduction

**Twilio** allows software developers to programmatically make and receive
phone calls and send and receive text messages using its web service APIs.

PokeAlarm offers the following for Twilio:

* Personalized notifications via [Dynamic Text Substitution](Dynamic-Text-Substitution)

## Basic Config

These `alarms.json` parameters are required to enable the alarm service:

### Required Parameters

| Parameters     | Description                            |
|:-------------- |:---------------------------------------|
|`type`          | must be `twilio`                       |
|`active`        | 'true' for alarm to be active          |
|`account_sid`   | Your Account SID from Twilio           |
|`auth_token`    | Your Auth Token from Twilio            |
|`from_number`   | Your Twilio number to send from        |
|`to_number`     | Your number to receive texts from      |

### Example: Basic Alarm Configuration using Required Parameters

```json
{
	"active":true,
	"type":"twilio",
	"account_sid":"YOUR_API_KEY",
	"auth_token":"YOUR_AUTH_TOKEN",
	"from_number":"YOUR_FROM_NUM",
	"to_number":"YOUR_TO_NUM"
}
```
**Note:** The above code is to be inserted into the alarms section of
alarms.json. It does not represent the entire alarms.json file.

## Advanced Config
In addition to the above required parameters, several optional parameters
are available to personalize your notifications.

### Multiple Destinations

The `to_number` field can accept either a single destination phone number
or an array of phone numbers to send SMS messages to. This allows for
sending SMS alerts to multiple destinations.

#### Example

Below is an example of using an array for the destination number(s) in the
alarm configuration.

```json
{
	"active":true,
	"type":"twilio",
	"account_sid":"YOUR_API_KEY",
	"auth_token":"YOUR_AUTH_TOKEN",
	"from_number":"YOUR_FROM_NUM",
	"to_number": [ "YOUR_1ST_TO_NUM", "YOUR_2ND_TO_NUM", "YOUR_3RD_TO_NUM" ]
}
```

### Optional Parameters

These optional parameters below are applicable to the `monsters`, `stops`,
`gyms`, `eggs`, and `raids` alarm code of the JSON file.

#### Optional Pokemon Parameters
| Parameters  | Description                     | Default                                                    |
|:------------|:--------------------------------|:-----------------------------------------------------------|
|`message`		| Text message for pokemon updates	| `"A wild <mon_name> has appeared! <gmaps> Available until <24h_time> (<time_left>)."` |

#### Optional Pokestop Parameters
| Parameters  | Description                            | Default																			                 |
|:------------|:---------------------------------------|:--------------------------------------------------------------|
|`message`		| Text message for pokestop updates		   | `"Someone has placed a lure on a Pokestop! <gmaps> Lure will expire at <24h_time> (<time_left>)."` |

#### Optional Gym Parameters
| Parameters  | Description                          | Default                                                       |
|:------------|:-------------------------------------|:--------------------------------------------------------------|
|`message`		| Text message for gym updates         | `"A Team <old_team> gym has fallen! <gmaps> It is now controlled by <new_team>."` |

#### Optional Egg Parameters
| Parameters  | Description                          | Default                                                       |
|:------------|:-------------------------------------|:--------------------------------------------------------------|
|`message`		| Text message for egg updates         | `"A level <egg_lvl> raid is incoming! <gmaps> Egg hatches <24h_hatch_time> (<hatch_time_left>)."` |

#### Optional Raid Parameters
| Parameters  | Description                          | Default                                                       |
|:------------|:-------------------------------------|:--------------------------------------------------------------|
|`message`		| Text message for raid updates        | `"Level <raid_lvl> raid against <mon_name>! <gmaps> Available until <24h_raid_end> (<raid_time_left>)."` |

#### Example: Alarm Configuration Using Optional Parameters

Below is an example of these optional parameters and how they are incorporated
into a functional alarm layout.

```json
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
```
**Note:** The above code is to be inserted into the alarms section of
alarms.json. It does not represent the entire alarms.json file.

## How to get the Account SID, Auth Token, and Twilio Number

1. Go to [Twilio](https://www.twilio.com) and click 'Get a free API key'.
Fill out the following form, and enter your phone number to verify your
account.

2. On the left hand side, click the Home Button and then click Dashboard.
The **Account SID** and **Auth Token** will be listed. To reveal the Auth
Token, click on the lock next to it.

3. Scroll down and click on '# Phone Numbers'. Then click 'Get Started'
to get your free number.

4. If you wish to text to different numbers, you need to register each before
you are allowed to message them. This can be done from the 'Verified Caller
ID's' page.
