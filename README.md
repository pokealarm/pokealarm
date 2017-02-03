#![PokeAlarm Logo](https://github.com/kvangent/PokeAlarm/wiki/images/logo.png) 

![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)
[![license](https://img.shields.io/github/license/kvangent/PokeAlarm.svg)]()
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5W9ZTLMS5NB28&lc=US&item_name=PokeAlarm&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)  
PokeAlarm is a third party extension of [RocketMap](https://github.com/RocketMap/RocketMap) that allows you to receive external notifications through a variety of services, such as Twitter, Facebook, Slack, or Discord.

#CONFIG CHANGES WARNING
PokeAlarm has recently updated to Version 3. This is a significant overhaul, and as such, some configuration changes may be required. 

## Features
* Receive notifications for Pokemon, Pokestops, and Gyms
* Supports a wide variety of external services such as Twitter, Slack, or Discord.
* Dynamic Text Substitution - customize your notifications to include a variety of options, include IV's, movesets, and more!
* Filter notifications based on location, moves, IV's, and more. 
* Reverse geocoding - Get the street adress, city, or zip code of a pokemon based on its location.
* Supports translations of Pokemon names and moves based on the following languages: DE, EN, ES, FR, IT, and ZH_HK
* Multiprocessing allows multiple managers to share a single listening port, reducing overhead.  

## Services
* [Boxcar](https://github.com/kvangent/PokeAlarm/wiki/Boxcar)
* [Discord](https://github.com/kvangent/PokeAlarm/wiki/Discord)
* [Facebook](https://github.com/kvangent/PokeAlarm/wiki/Facebook-Pages)
* [Pushbullet](https://github.com/kvangent/PokeAlarm/wiki/Pushbullet)
* [Pushover](https://github.com/kvangent/PokeAlarm/wiki/Pushover)  
* [Slack](https://github.com/kvangent/PokeAlarm/wiki/Slack)
* [Telegram](https://github.com/kvangent/PokeAlarm/wiki/Telegram) 
* [Twilio (SMS)](https://github.com/kvangent/PokeAlarm/wiki/Twilio-(SMS))
* [Twitter](https://github.com/kvangent/PokeAlarm/wiki/Twitter)

## Support
### Wiki
Please read the [**Wiki**](https://github.com/kvangent/PokeAlarm/wiki) before contacting us for support. It should answer all your questions about installation and configuration.

### Discord
Visit us at our [**Discord channel**](https://discord.gg/TNcqsRr) if you still have issues with your setup. Please stick to the `#troubleshooting` and `#general` chats and avoid sending private messages to any developers. We're working hard, we promise!

### Github
If you are experiencing issues with the alarm or would like to see new features, please open a ticket on github [here](https://github.com/kvangent/PokeAlarm/issues/new). Be sure to complete the included suppport template and provide as much information as possible.  **Support tickets that do not fully complete the request template WILL be closed without notice.**

## FAQ
#### I am receiving an error about JSON input from PokeAlarm (e.g., "expecting delimiter"). What gives?
* If you are a Windows user, stop using notepad and start using Notepad++. Make a fresh copy of the alarms.json and remake your changes. If you aren't a Windows user (or you are already using Notepad++) check your JSON format with a JSON formatter for issues ([jsoneditoronline.org](http://www.jsoneditoronline.org) is an excellent site to start.)

#### Will you be adding support for ______ service?
* Please make a request in the [NEW/UPCOMING SERVICE MEGA-THREAD](https://github.com/kvangent/PokeAlarm/issues/147).  New standalone issue tickets will be closed without notice.

#### I am receiving _______ error from PokemonGo-Map! What do I do?
* Checkout the [PokemonGo-Map Wiki](https://github.com/kvangent/PokeAlarm/wiki) or try asking for help in our [Discord channel](https://discordapp.com/invite/am66rag).

#### How do I conigure V3?
* We are working on updating the wiki to reflect the changes. Use the `filters.json` file to specify which notifications you would like to receive. The 'alarms.json' file is now for specifying which services you would like to receive alerts from. 
