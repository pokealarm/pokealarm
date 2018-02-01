# Rules

## Overview

* [Prerequisites](#prerequisites)
* [Default Rule](#default-rule)
* [Creating Custom Rules](#creating-custom-rules)
* [Examples](#examples)

## Prerequisites

This page assumes:

1. You have a working PA installations.
2. You read and understood the [Filters](Filters-Overview) page.
3. You read and understood the [Alarms](alarms) page
4. You have an understanding on what a [Manager](Managers) is.

## Default Rule

Normally when PA is processing an Event, it goes through the Filters in
the order listed. Once it finds a match, it triggers all of the Alarms
attached to that manager.

Imagine you have some filters( `"100-iv"`, `"90-iv"`,
`"in_geofence"`, `"rare-mon"`) and some alarms (`"discord-rare"`,
`"discord-perfect"`, `"telegram-all"`). First, PA will check the `"100-iv"`
filter. If that doesn't match, it will check the `"90-iv"` filter.
Once it finds a match, it will then send to all of the alarms.

This behavior is known as the 'default rule' - all filters to all
alarms. If you don't specify any rules for a section, this is the
default behavior. The 'default rule' for the above scenario could be
 described as the following:

```json
"default": {
    "filters": ["100-iv", "90-iv", "in_geofence", "rare-mon"],
    "alarms": ["discord-rare", "discord-perfect", "telegram-all" ]
}

```

Each rule has a name, and 2 required sections: `"filters"` and
`"alarms"`. Each section is simply a list of names corresponding to the
appropriate section. Sections are required, and you will be unable to
make a rule to a filter or alarm that doesn't exist.

## Creating Custom Rules

You can specify your own rules to override the defaults. This can be
done by setting `--rules rules.json` or `rules: rules.json` in the
config.ini.

Each rule file can have 5 sections, one for each type of event. An empty
rules file would look like this, and would results in the default rules:
```json
{
    "monsters": {
    },
    "stops": {
    },
    "gyms": {
    },
    "eggs": {
    },
    "raids": {
    }
}
```

Adding rules will override the default rules and create new behavior.
If multiple rules are specified, they will be checked independently and
possible trigger a notification for each one. For example, the
following would send `"rare-mon"` events to the telegram alarm,  and all
other events to the discord alarm.

```json
{
    "monsters": {
        "discord-rule": {
            "filters": [ "100-iv", "90-iv", "in_geofence" ],
            "alarms": [ "discord-rare", "discord-perfect" ]
        },
        "telegram-rule": {
            "filters": [ "rare-mon" ],
            "alarms": [ "telegram-all" ]
        }
    }
}
```

## Examples

Coming soon!

