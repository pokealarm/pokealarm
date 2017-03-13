#![PokeAlarm Logo](https://github.com/kvangent/PokeAlarm/wiki/images/logo.png) 

![Python 2.7](https://img.shields.io/badge/python-2.7-blue.svg)
[![license](https://img.shields.io/github/license/kvangent/PokeAlarm.svg)]()  
PokeAlarm is a third party extension of [RocketMap](https://github.com/RocketMap/RocketMap) that allows you to receive external notifications through a variety of services, such as Twitter, Facebook, Slack, or Discord.

### Support PokeAlarm [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=5W9ZTLMS5NB28&lc=US&item_name=PokeAlarm&currency_code=USD&bn=PP%2dDonationsBF%3abtn_donateCC_LG%2egif%3aNonHosted)  [![Donate](https://img.shields.io/badge/Donate-Patron-orange.svg)](https://www.patreon.com/bePatron?u=5193416)  
If you like PokeAlarm, and enjoying seeing updates and new features added, consider donating to us. Donating to PokeAlarm helps cover the costs of running my own maps (which I need to test PokeAlarm) and lets me spend more time working on PokeAlarm instead of on something else.



#CONFIG CHANGES WARNING
PokeAlarm is now on v3.1. For an overview of what has changed, please check out the latest [Patch Notess](https://github.com/kvangent/PokeAlarm/wiki/patch_notes).

## Features
* Receive notifications for Pokemon, Pokestops, and Gyms
* Supports a wide variety of external services such as Twitter, Slack, or Discord.
* Dynamic Text Substitution - customize your notifications to include a variety of options, include IV's, movesets, and more!
* Filter notifications based on location, moves, IV's, and more. 
* Reverse geocoding - Get the street adress, city, or zip code of a pokemon based on its location.
* Supports translations of Pokemon names and moves based on the following languages: DE, EN, ES, FR, IT, and ZH_HK
* Multiprocessing allows multiple managers to share a single listening port, reducing overhead.  

## Services
* [Discord](Discord)
* [Pushbullet](Pushbullet) 
* [Slack](Slack)
* [Telegram](Telegram) 
* [Twilio (SMS)](Twilio)
* [Twitter](Twitter)
* [Facebook Pages](Facebook-Pages)

## What exactly is PokeAlarm?

PokeAlarm is a lightweight webserver designed to receive POST requests from your local RocketMap server. It sorts through these request and send your a message via your favorite message service.  This could be either a tweet when a rare pokemon spawning down the street, a Telegram message letting you know a lured pokestop only a few minutes away, or a Pushbullet notification letting you know your team's gym has fallen.

## Support

#### Wiki
Please read the [**Wiki**](https://github.com/kvangent/PokeAlarm/wiki) and the FAQ below before contacting us for support. It should answer all your questions about installation and configuration. Make sure to check out the sidebar on the right.

#### Discord
Visit us at our [**Discord channel**](https://discord.gg/TNcqsRr) if you still have issues with your setup. Please stick to the `#troubleshooting` and `#general` chats and avoid sending private messages to devs. We're working hard, we promise!

#### Github
If you are experiencing issues with the alarm or would like to see new features, please open a ticket on github [here](https://github.com/kvangent/PokeAlarm/issues/new). Be sure to complete the included suppport template and provide as much information as possible.  **Support tickets that do not fully complete the request template may be closed without notice.**

## FAQ

#### I am receiving an error about JSON input from PokeAlarm. What gives?

* If on Windows, DON'T USE NOTEPAD. Use Notepad++ or PyCharm. Create a new `alarms.json` and start over. Alternatively, use [jsoneditoronline.org](http://www.jsoneditoronline.org) to check for errors.

#### Which version of RocketMap do I need?

* Use the develop branch of RocketMap.  PokeAlarm is a webhook - an extension of RocketMap. We can update PokeAlarm without affecting your RocketMap installation (and vice-versa).  

#### How do I request for a Service to be added to PokeAlarm?
* Please make a request in the [NEW/UPCOMING SERVICE MEGA-THREAD](https://github.com/kvangent/PokeAlarm/issues/147).

#### Man I wish this could do XYZ!
* Open an Enhancement Request on github. Do not PM us!

#### I am receiving XYZ error from RocketMap! What do I do?
* Check the [RocketMap Wiki](https://rocketmap.readthedocs.io) or the ask in the RocketMap Discord.  We will not troubleshoot your RocketMap installation.

#### Can I run multiple simultaneous alarms services?

* Yes. You may configure as few or as many simultaneous alarm services in `alarms.json` like Twitter, Discord and Telegram.  Visit the Alarm Configuation wiki for more details.

Alternatively, you can run RocketMap with multiple webhooks and have multiple instances of PokeAlarm, each assigned to a different `http://<host>:<port>`, e.g., `http://127.0.0.1:4000`, `http://127.0.0.1:4001`.

#### I'm having issues with setting a location. It is not showing distance, maps are not showing up, walking directions, etc.

* Ensure you have a Google Maps API key with all the necessary APIs enabled. Visit the Google Maps API Key wiki on how to test your key and more details.
