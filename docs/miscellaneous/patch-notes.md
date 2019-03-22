# Patch Notes

## Patch History

* [Patch 3.8](#patch-3-8)
* [Patch 3.7](#patch-3-7)
* [Patch 3.6](#patch-3-6)
* [Patch 3.5](#patch-3-5)
* [Patch 3.4](#patch-3-4)
* [Patch 3.3](#patch-3-3)
* [Patch 3.2](#patch-3-2)
* [Patch 3.1](#patch-3-1)

---

## Patch 3.8

### Server Settings
* **Logging Rework**
  * The 'main' logger represents logging from the entire application,
    including webserver and managers that are attached.
  * `log-lvl`- Verbosity of the main logger (default=3)
  * `log-file` - File path of the main logger
    (default='logs/pokealam.log')
  * `log-size` - Maximum size (in mb) of a log before rollover
  * `log-ct` - Maximum number of older logs to keep.
  * The 'manager' loggers are attached to each individual manager
  * `mgr-log-lvl` - Verbosity of a manager's logger (default=3)
  * `mgr-file-lvl` - Path of a file to attach to a manager's logger.
  * `mgr-log-size` - Maximum size (in mb) of a log before rollover
  * `mgr-log-ct` - Maximum number of older logs to keep.

### Events
* **All Events**
  * Added `waze` dts to provide a deep link to the event location in the
    Waze app
* **Monsters**
  * Added `rarity` dts for scanners that properly support dynamic rarity
    via webhook.
* **Weather**
  * Added a new Event to handle weather changes! This event represents
    a a change in weather for a location. For more information check out
    the [Weather Events](../configuration/events/weather-events.html)
    page.

### Filters
* **Monsters**
  * Added `rarity` restriction for scanners that properly support
    dynamic rarity via weebhook.
* **Weather**
  * Added a filters to handle the new Weather Events. For more
    information check out the
    [Weather Filters](../configuration/filters/weather-filters.html)
    page.

### Alarms
* No changes

### Misc
* No changes

## Patch 3.7

### Server Settings
* **File Cache Improvements**
  * Decreased chance of corrupted cache if shutdown improperly
  * Overwrites corrupted cache if detected, rather than throw error
* **Gmaps Clean Up**
  * Automatic enabling for GMaps related DTS has been removed. Instead,
    you will need to manually enable these DTS via server settings. See
    the `config.ini.example` for usage.
  * Fixed a bug where API Quotas caused timeouts
  * Config change: `key` changed to `gmaps-key`
  * `<walk_dist>` changed to `<walking_distance>`
  * `<walk_time>` changed to `<walking_duration>`
  * `<bike_dist>` changed to `<biking_distance>`
  * `<bike_time>` changed to `<biking_duration>`
  * `<drive_dist>` changed to `<driving_distance>`
  * `<drive_time>` changed to `<driving_duration>`
  * `<transit_distance>` added
  * `<transit_duration>` added
* **Example Config Updated**
  * `config.ini.example` has been cleaned up and updated for
    readability.

### Events

* **Monsters**
  * Costume DTS: `costume`, `costume_or_empty`, `costume_id`,
    `costume_id_3`
  * Move Type DTS: `quick_type_id`, `quick_type`, `quick_type_emoji`,
    `charge_type_id`, `charge_type`, `charge_type_emoji`
  * Moveset Quality DTS: `atk_grade` and `def_grade `
  * Catch Rate DTS: `base_catch`, `great_catch`, `ultra_catch` (and
    precision variants)
  * Added precision variants for `height` and `weight` DTS
  * Added support for RM supported weather

* **Eggs**
  * Park DTS: `park`
  * Sponsor DTS: `sponsor_id`, `sponsored`

* **Raids**
  * Form DTS: `form`, `form_or_empty`, `form_id`, `form_id_3`
  * Park DTS: `park`
  * Sponsor DTS: `sponsor_id`, `sponsored`

### Filters

* **All**
  * Custom DTS improved - filter level now combines with defaults rather
    than replace
  * Bugfix: Geofences now always evaluate in order listed

* **Monsters**
  * `monsters_exclude` restriction - list of monsters to ignore, by id
    or name
  * `costume_ids` restriction - restrict by costume id

* **Gyms**
  * `gym_name_excludes` restriction - restrict gym_name to not contain
    a matching regex

* **Eggs**
  * `gym_name_excludes` restriction - restrict gym_name to not contain
    a regex match
  * `sponsored` restriction - restrict sponsor_id to be zero or not
  * `park_contains` restriction - restrict park to contain a regex match

* **Raids**
  * `monsters_exclude` restriction - list of monsters to ignore, by id
    or name
  * `gym_name_excludes` restriction - restrict gym_name to not contain
    a matching regex
  * `sponsored` restriction - restrict sponsor_id to be zero or not
  * `park_contains` restriction - restrict park to contain a regex match

### Alarms

* **Telegram**
  * `web_preview` parameter - enable/disable web previews for messages

### Misc
* Minor fixes for `zh-hk` size translations.



---

## Patch 3.6

This patch contains several breaking changes - make sure to read
carefully, back up your current configuration, and have some free time
before attempting to upgrade.

### Rules (Optional)

**New Feature** - The "Rules" feature will allow users to create rules
that dictate which filters trigger which alarms. Rules are loaded via
a file containing a json object, which has 5 sections similar to the
Filters file. Each section is a key-value pair of "rule names" to "rules".
Each rule can be described as a json object containing just two fields:
"filters" and "alarms". Each field is an array of strings corresponding to
the name of a filter or alarm from a manager. Rules cannot be loaded if
they do not match an existing filter or alarm.

Rules are evaluated by checking the listed filters one by one (in order),
until a match is found. Once a match is found, PA will them notify each alarm
listed in the Rule. **Every** rule is always evaluated **every** time.

Rules are an optional configuration setting and if no rules are set then PA
will check every filter in the order that they are listed in the filters file
and will target every alarm.

Rules can be loaded via a rules file with `-r` and `--rules` via commandline
or `rules: rules.json` in config.ini.

Each rules file must be configured key-value objects and contain at least one
or more of following rules sections:

* `monsters`
* `stops`
* `gyms`
* `eggs`
* `raids`

The inner section of each rule must be configured as a key-value object where
the key is the rule's name, and the value is the rule's setting.

Each rule can be described as follows:

```json
"example_rule" : {
    "filters": [ "filter1", "filter2" ],
    "alarms": [ "alarm1", "alarm2" ]
}
```

### Alarms

**Breaking Changes** - To fully take advantage of the "Rules" feature, the
"Alarms" feature was changed to require a key-value json object instead of
a list. Alarms should now be a list of "name" -> "alarm settings".
The alarms.json.example has been updated to match this.

#### Changed Alert Sections

The Alert sections of alarms has been updated to match the event names:

* `pokemon` -> `monsters`
* `pokestop` -> `stops`
* `gym` -> `gyms`
* `egg` -> `eggs`
* `raid` -> `raids`

#### Alerts Converter

A new tool has been added to `tools/convert_alarms_file.py`, this tool is
designed to convert Alerts files from 3.5 and prior to the 3.6 alert format.

**Usage**:

```bash
python convert_alarms_file.py /path/to/alarms.json
```

#### Telegram Changes

**Breaking Changes** - Telegram alarms have been reworked to resolve multiple
issues and address Telegram API changes.

* **Content Changes** - Telegram now uses markdown instead of html to reduce
conflicts caused by using invalid DTS fields. Existing alerts will have to be
reconfigured to make this change.
  * The `venue` field does not support markdown or html coding
  * `title` and `body` have been merged into `message` to better represent how
  the Telegram API actually treats messages. The old behavior can be mimiced
  by using the following example content: `*TITLE GOES HERE*\n BODY GOES HERE`
* **Field Changes** - The following fields have been changed:
  * `bot_token`: Can now be set at an Alert level. DTS compatible.
  * `chat_id`: Now DTS compatible.
  * `stickers` -> `sticker`: Set to "true" for sticker with message,
 set to "false" for no sticker.
  * `sticker_notify`: Whether or not sticker messages causes a notification.
  * `sticker_url`: Url to be used for the sticker. Must be .webp file.
  * `location` -> `map`: true for map after message, false for no map.
  * `map_notify`: Whether or not map messages causes a notification.
  * `venue`: Sends the map and message in a single condensed format.
  * `venue_notify`: Whether or not venue messages causes a notification.
  * `max_retries`: Max attempts to send for each message.
 (Telegram no longer uses the command line equivalent)

### Filters

* Listed filters now evaluate in the order listed in the file.
* The `"geofences" : [ "all" ]` shortcut now evaluates in the order that the
geofences are listed in the geofence file.
* `gym_name_contains` is now case-insensitive.

#### Time Based Filtering

Filters now support filtering based on event timing.  This allows for
greater control over event alerts than what was previously supported via the
`timelimit` configuration option.

* **New Filters**
  * `min_time_left` - The minimum amount of time in seconds until the event
	* `max_time_left` - The maximum amount of time in seconds until the event
* **Filter Events**
  * **Monsters** - Filters based on time until monster despawns
	* **Stops** - Filters based on time until the lure ends
	* **Raids** - Filters based on time until the raid ends
	* **Eggs** - Filters based on time until the egg hatches

### Locale

* Added multi-lingual support for the `Size` DTS & Filter setting.

### Dynamic Text Substitutions

* **Monsters & Raids**
  * `size` - Changed to support locales
  * `weather` - Outputs the current weather conditions in the alert
	* `weather_id` - Outputs the current weather condition id
	* `weather_or_empty` - Same as `weather` or an empty value
	* `weather_emoji` - Outputs a unicode emoji for the current weather
  * `boosted_weather` - Outputs the weather conditions if boosted
	* `boosted_weather_id` - Outputs the boosted weather condition id
	* `boosted_weather_or_empty` - `boosted_weather` or an empty value
	* `boosted_weather_emoji` - Outputs an emoji for the boosted weather
	* `boosted_or_empty` - Outputs the word **boosted** if Raid/Mon is boosted
	* `type1` - Outputs the name of the Monster's Primary Type or `?`
	* `type1_or_empty` - Same as `type1` or an empty value
	* `type1_emoji` - Outputs an emoji for the Monster's Primary Type or Empty
	* `type2` - Outputs the name of the Monster's Secondary Type or ?
	* `type2_or_empty` - Same as `type2` or an empty value
	* `type2_emoji` - Outputs an emoji for the Monster's Primary Type or Empty
	* `types` - Outputs the Monster's Type formatted as "type1/type2"
	* `types_emoji` - Outputs an emoji for the Monster's Type(s) or Empty

* **Eggs**
  * `weather` - Outputs the current weather conditions in the alert
	* `weather_id` - Outputs the current weather condition id
	* `weather_or_empty` - Same as `weather` or an empty value
	* `weather_emoji` - Outputs an emoji for the current weather conditions

### Server Settings

* **Performance Fixes** - Users should now see improved performance
  and less system resource usage overall.

### Bug Fixes

* **Twitter Alarms**
  * Maximum length has been extended to 280 characters to match Twitter
	 standards and settings
	* All URLs are now counted as 23 characters towards the overall
	 character limit detection. URLs that would cause the tweet to exceed
	 280 characters will be dropped from the tweet.
	* DTS is now evaluated before the length of the status update is
	 calculated. This corrects issues with improper Twitter Status Truncation

---

## Patch 3.5

This patch contains several breaking changes - make sure to read
carefully, back up your current configuration, and have some free time
before attempting to upgrade.

### Filters

**Breaking Changes** - Filters have been completely reworked, with the
design focused on reducing managers and optimizing system resources.
Several filter parameter's have changed or been updated. For full
instructions on the new system, please see the new
[Filters](Filters-Overview) page in the wiki.

Some highlights include:

    * Custom DTS - new feature to define filter specific DTS

### Server Settings

* Added `concurrency` setting - Determines the maximum number of
concurrent connections PA will accept. Lowering this may help lower-end
systems improve the response time for their machines.

### Alarms

* **All**
    * Updated default image urls for `icon_url` and `avatar_url`. These
    default urls have built in cache busting

* **Discord**
    * `webhook_url` field is now DTS compatible

* **Twilio**
    * Now supports using an array of numbers for the `to` field in Alert
     configurations.

### Dynamic Text Substitutions

* **Pokemon**
    * `enc_id` changed to `encounter_id`
    * `level` changed to `mon_lvl`
    * `pkmn` changed to `mon_name`
    * `pkmn_id` changed to `mon_id`
    * `pkmn_id_3` changed to `mon_id_3`
    * `form_id_3_or_empty` replaced with `form_id_3`
    * `tiny_rat` - Updated to use weight instead of size.
    * `big_karp` - Updated to use weight instead of size.

* **Pokestops**
    * `id` changed to `stop_id`

* **Raids**
    * `team_leader` - Reports the name of the team leader of the team in
     control of the gym.
    * `pkmn` changed to `mon_name`
    * `raid_level` changed to `raid_lvl`
    * `time_left` changed to `raid_time_left`
    * `24h_time` changed to `24h_raid_end`
    * `gym_image_url` changed to `gym_image`

* **Eggs**
    * `raid_level` changed to `egg_lvl`
    * `begin_time_left` changed to `hatch_time_left`
    * `time_left` changed to `raid_time_left`
    * `begin_12h_time` changed to `12h_hatch_time`
    * `begin_24h_time` changed to `24h_hatch_time`
    * `gym_image_url` changed to `gym_image`

* **Gyms**
    * `gym_image_url` changed to `gym_image`
    * `slots_available` - displays the number of open guard slots
    available in a gym
    * `guard_count` - displays the number of guards assigned to a gym    

### Misc

* Added Gen3 Move information
* Updated Kyogre and Groudon stats
* Added Portuguese language translations - `pt`

---

## Patch 3.4

### Server Settings

* Implemented caching for managers with `-ct` or `--cache_type`. Cache is used to handling remembering things like pokemon history and gym names.
    * (default) `mem` - data persists only in memory.
    * `file` - data is saved and loaded from a file.
* PA now gracefully exits on ctrl+c, finishing items in queue and logging the status of managers.

### Dynamic Text Substitutions

* **All**

    * `lat_5` and `lng_5` - Latitude and Longitude for the event, truncated to 5 decimal places.
    * `address_eu` - same as `<street> <street_num>`.

* **Pokemon**

    * `form_or_empty` - Reports the form name of the pokemon if known, or an empty string if unknown.
    * `pkmn_id_3` - pokemon id padded to 3 digits.
    * `form_id_or_emtpy` - prints form_id padded to 3 digits if known, or and empty string if unknown.

* **Raids**
    * `form_or_empty` - Reports the form name of the pokemon if known, or an empty string if unknown.
    * `team_name` - Reports the current team for a Raid gym if known, or 'unknown' if not.
    * `team_id` - Reports the current team id for a Raid gym if known, or '?' if not.
    * `min_cp` and `max_cp` - min and max potential cp for the raid boss if caught.
    * `pkmn_id_3` - pokemon id padded to 3 digits.
    * `form_id_or_emtpy` - prints form_id padded to 3 digits if known, or and empty string if unknown.

### Tools

* Webhook Tester
    * Added `webhook_tester.py` for users to simulate sending events.

---

## Patch 3.3

### Dynamic Text Substitution
* **Pokemon**
    * (Re) added `'form'` DTS (and made it more robust).

#### Server Settings
* **Reverse Location**
    * Location services have been completely reworked to be more reliable.
    * Location results now retrieve results set in whatever language is set for that manager.
    * Location results now cache in memory - lowering overall API usage.

---

## Patch 3.2

#### Filters
* **Pokemon**
    * Pokemon can now be filtered by their form_id (example": `"form": [0, 1, 2]`).
    * Pokemon can now be filtered by their gender (example": `"gender": ["male", "female"`).
    * `'min_cp'` and `'max_cp'` are used to limit the CP of pokemon to alert.
* **Egg**
    * "Egg" section is now added to the filters.json.
    * `'enabled'` allows incoming raid alerts to be toggled on or off.
    * `'min_level'` and `'max_level'` are used to limit the levels of incoming raids to alert on.
* **Raids**
    * "Raids" section is now added to the filters.json.
    * `'enabled'` allows raid alerts to be toggled on or off.
    * `'default'` allows setting default settings for filters, and has the same options as pokemon filters do.
    *  Filters for pokemon raids can be set similar to the "pokemon" section, with the `"name": {}` scheme.

#### Dynamic Text Substitution
* **General**
    * Added `'applemaps'` to most alerts for AppleMaps link for iOS users.
    * Time DTS now switch to ##h##m format when longer than one hour.
* **Pokemon**
    * Added support for the following substitutions: `'cp', 'form', 'form_id', 'level'`.
    * Added `'big_karp'` that displays 'big' on big magikarp and `'tiny_rat'` that displays 'tiny' on small rattata.
* **Egg**
    * "Egg" alerts have the following substitutions: `'type', 'id', 'raid_level', 'raid_end', 'raid_being', 'lat', 'lng', 'gym_name', 'gym_description', 'gym_url'`.
* **Raid**
    * "Raid" alerts have the following substitutions: `'type', 'id', 'pkmn_id', 'cp', 'quick_id', 'quick_damage', 'quick_dps', 'quick_duration', 'quick_energy', 'charge_id', 'charge_damage', 'charge_dps', 'charge_duration', 'charge_energy', 'raid_level', 'raid_end', 'raid_begin' 'lat', 'lng', 'gym_name', 'gym_description', 'gym_url'`.
* **Gyms**
    * Added the following Gym substitutions: `'name', 'description', 'url'`.
    * Added the following 'Gym Leader' substitutions: `'old_team_id', 'new_team_leader', 'old_team_leader'`.

#### Alarms
* **Twitter**
    * Twitter now automatically truncates to 140 characters - it will preserve <gmaps> links if added to the end.
* **Discord**
    * Discord usernames now automatically truncates usernames to 32 characters.
    * Added `'avatar_url'` to change the avatar of the post.
    * Added `content` field that posts a message before the embed, allows for taging by user or roll.
    * Added `'disable_embed'` that disables the discord embeds when set to `true`.

---

## Patch 3.1

#### Filters
* **Multifilters** - Each filter can now be one of the following:
     * `'True'` for all defaults, `'False'` for entirely disabled.
     * A single filter in a json object (Ex: `{ "min_iv":"0",  "max_iv" : "0" ... }`).
     * Multiple filters inside an array: `[{"min_iv":"0", "max_iv":"25" }, {"min_iv":"75", "max_iv":"100"} ]`.

* **Pokemon**
    * All default filter parameters are now encapsulated in a single filter under the label `default`.
     * `size` requires an array of valid sizes from the following: `['tiny', 'small', 'normal', 'large', 'big']`.
     * `move_1` and `move_2` are now `quick_move` and `charge_move`.
     * `size`, `quick_move`, `charge_move`, `moveset` filter parameters will accept any value when set to `null`.

* **Pokestops**
    * Now only two fields: `enabled` and `filters`.
    * `filters` supports the Multifilter format with `min_dist` and `max_dist` fields.

* **Gym**
    * Now only three fields `enabled`, `ignore_neutral`, and `filters`.
    * `filters` supports multifilters with the following fields:
        * `from_team` - Array of valid previous team names.
        * `to_team` - Array of valid current team names.
        * `min_dist` and `max_dist` working as before.

#### Dynamic Text Substitution
* `<geofence>` added - the name of the first geofence in which the notification is in.
* `<size>` now list either `'tiny'`, `'small'`, `'normal'`, `'large'`, or `'big'`.
* Quick moves now use the following:  `<quick_move>`, `<quick_id>`, `<quick_damage>`, `<quick_dps>`, `<quick_duration>`, `<quick_energy>`.
* Charges moves now use the following: `<charge_move>`, `<charge_id>`, `<charge_damage>`, `<charge_dps>`, `<charge_duration>`, `<charge_energy>`.

#### Alarms
* All Services
    * `startup_list` is officially gone.
* Boxcar
    * No longer supported.
* Discord
    * `api_key` renamed to `webhook_url`.
    * Will now retry if webhook was not received correctly.
    * New optional alarm and alert level field: `map`.
        * `enabled` - True of False to enabled/disabled map.
        * Added other static map parameters.
* Slack
    * `channel` parameter is now required at the Alarm level.
        * Slack will no longer default to general if the correct channel cannot be found.
        * Slack will still default to the Alarm level channel over the Alert level channel is not found (so everyone can still use `<pkmn>`!).
* Pushover
    * No longer supported.
