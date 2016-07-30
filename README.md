# PokeAlarm

The alarm is a third party extenstion of [AHAAAAAAA's PokemonGo-Map](https://github.com/AHAAAAAAA/PokemonGo-Map) that allows you to received external notifications via the service of your choice.

We currently support Pushbullet, Slacker, Twilio (SMS), and Telegram. Pushbullet support will likely be dicontinued after August 1st (because I am a poor college student). 

If you are experience issues with the alarm or would like to see new features, please open a ticket here on github. 

If you are experiencing trouble with setup or other user difficulties, please see the reddit thread.

## Setup

1. Setup and run [AHAAAAAAA's PokemonGo-Map](https://github.com/AHAAAAAAA/PokemonGo-Map) to make sure you have everything working.

2. Clone a local copy of PokeAlarm (`git clone https://github.com/kvangent/PokeAlarm`) and navigate inside the folder.

3. Run pip to install requirments `pip install -r requriements`

4. Copy alarms.json.default and rename it alarms.json. Edit the file (Windows User's: NOT with notepad) with your configuration settings. Make sure to change the pokemon you want to be alerted to "True". Each alarm configuration will be added to the wiki shortly. All the fields are required except for the 'name' field - it can be left blank or not included in the config at all.

5. Start the webhook server with `python runwebhook.py`. You should receivea  notification if your alarm is set up correctly. You can specify a host and port with `-H HOST -P PORT`. The default is a host of 127.0.0.1 and port of 4000.

6. When you start the PokemonGo-Map, add the argument `-wh http://127.0.0.1:4000` (with the appropriate host and port). You may also set this up in PokemonGo-Map's config.ini (just make sure you remove the hash and don't use qoutations).

7. If your PokeAlart process is receiving hits, you are all set! Go catch 'em all!

## FAQ

Q. Which version of PokemonGo-Map do I need?
A. Either dev or master, both have included webhook support. This program is an exstension, so we can update one without affecting the other. The master branch is more stable, so I would reccomend that. 

Q. Will you be adding support for XXX?
A. Open a ticket with a link to the Service API you are interested in and I will see what I can do.

Q. Man I wish this could do XXX!
A. Open an issue request and I will look into it. (Or do it yourself and open a pull request

Q. I am receiving XXX error from PokemonGo-Map! What do?
A. Checkout AHAAAAAAA's Wiki or the reddit thread to see if anyone has any suggestions for you.

Q. I am receiving error about JSON input from PokeAlarm?
A. If you are a Window's user, stop using notepad and start using Notepad++. Make a fresh copy of the alarms.json and remake your changes. If you aren't a Window's user (or you are already using Notepad++) check your JSON format with a JSON formatter for issues.
