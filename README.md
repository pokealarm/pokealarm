#PokeAlarm

PokeAlarm is a third party extension of [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) that allows you to receive external notifications via one or more message services.  Customized notifications are available by configuring the `alarms.json` file.

![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)
[![license](https://img.shields.io/github/license/kvangent/PokeAlarm.svg)]()
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5W9ZTLMS5NB28&lc=US&item_name=PokeAlarm&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)  

We currently support the following services:
* [Pushbullet](https://github.com/kvangent/PokeAlarm/wiki/Pushbullet) (support likely be discontinued soon due to changes in the API pricing structure)
* [Pushover](https://github.com/kvangent/PokeAlarm/wiki/Pushover)  
* [Slack](https://github.com/kvangent/PokeAlarm/wiki/Slack)
* [Telegram](https://github.com/kvangent/PokeAlarm/wiki/Telegram) 
* [Twilio (SMS)](https://github.com/kvangent/PokeAlarm/wiki/Twilio-(SMS))
* [Twitter](https://github.com/kvangent/PokeAlarm/wiki/Twitter)

## Support

### Wiki
Please read the [**Wiki**](https://github.com/kvangent/PokeAlarm/wiki) before contacting us for support. It should answer all your questions about installation and configuration.

### Discord
Visit us at our [**Discord channel**](https://discordapp.com/invite/am66rag) if you still have issues with your setup. Please stick to the `#troubleshooting` and `#general` chats and avoid sending private messages to devs. We're working hard, we promise!

### Github
If you are experiencing issues with the alarm or would like to see new features, please open a ticket on github [here](https://github.com/kvangent/PokeAlarm/issues/new). Be sure to complete the included suppport template and provide as much information as possible.  **Support tickets that do not fully complete the request template may be closed without notice.**

## What exactly is PokeAlarm?

PokeAlarm is a lightweight webserver designed to receive POST requests from your local PokemonGo-Map server. It sorts through these requests, letting you know through your favorite service something has happend. It might be a tweet when a rare pokemon spawning down the street, a Telegram message letting you know a lured pokestop only a few minutes away, or else a Pushbullet notification letting you know your teams gym has fallen.

## FAQ

#### Which version of PokemonGo-Map do I need?

* Use the develop branch.  Most work in PokemonGo-Map is being done there.  They do not currently have a master. PokeAlarm is a webhook - an extension of PokemonGo-Map. We can update PokeAlarm without affecting your PokemonGo-Map installation, or vice-versa.  

#### Will you be adding support for XYZ?
* Please make a request in the [NEW/UPCOMING SERVICE MEGA-THREAD](https://github.com/kvangent/PokeAlarm/issues/147).  New standalone issue tickets will be closed without notice.

#### Man I wish this could do XYZ!
* Open an issue on github and fill out the appropriate issue template and we'll look into it.

#### I am receiving XYZ error from PokemonGo-Map! What do I do?
* Visit our [Discord channel](https://discordapp.com/invite/am66rag), Checkout the [PokemonGo-Map Wiki](https://github.com/kvangent/PokeAlarm/wiki) or the reddit thread to see if anyone has any suggestions for you.

#### I am receiving an error about JSON input from PokeAlarm (e.g., "expecting delimiter"). What gives?

* If you are a Windows user, stop using notepad and start using Notepad++. Make a fresh copy of the alarms.json and remake your changes. If you aren't a Windows user (or you are already using Notepad++) check your JSON format with a JSON formatter for issues ([jsoneditoronline.org](http://www.jsoneditoronline.org) is an excellent site to start.)

#### Can I run multiple simultaneous alarms services?

* Yes. You may configure as few or as many simultaneous alarm services in `alarms.json` like Twitter, Slack and Telegram.  For example, you can post to 2 Twitter accounts, 3 Slack channels and have a Twilio SMS service running from one `alarms.json` configuration. Visit the Alarm Configuation wiki for more details.

Alternatively, you can run PokemonGo-Map with multiple webhooks and have multiple instances of PokeAlarm, each assigned to a different `http://<host>:<port>`, e.g., `http://127.0.0.1:4000`, `http://127.0.0.1:4001`, `http://127.0.0.1:4002`.

#### I'm having issues with setting a location, it is not showing distance, maps are not showing up, walking directions, etc.

* These errors are Google Maps API related. Ensure you have an API key with all the necssary APIs enabled.  Visit the Google Maps API Key wiki for more details.
