# Fork of PokeAlarm with support for blynk

PokeAlarm is a third party extension for [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) that allows you to receive external notifications via the service of your choice.

The following services are currently supported in this fork:
* Pushbullet
* Pushover
* Slacker
* Telegram 
* Twilio (SMS)
* blynk

## Setup

1. Setup and run [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) to make sure you have everything working.

2. Clone a local copy of PokeAlarm (`git clone https://github.com/kvangent/PokeAlarm`) and navigate inside the folder.

3. Run pip to install requirements `pip install -r requirements.txt`

4. Copy alarms.json.default and rename it to alarms.json. Edit the file (Windows Users: NOT with notepad) with your configuration settings. Make sure to change the pokemon you want to be alerted to "True". Each alarm configuration will be added to the wiki shortly. All the fields are required except for the 'name' field - it can be left blank or not included in the config at all. You can also add multple of the same alarm type.  You can specify a different configuration file with `-cn <config_file.json>`.

5. Start the webhook server with `python runwebhook.py`. You should receive a notification if your alarm is set up correctly. You can specify a host and port with `-H HOST -P PORT`. The default is a host of 127.0.0.1 and port of 4000. This is the port that the webhook will listen on. The port number MUST be different to what you run your PokemonGo-Map server on!

6. When you start the PokemonGo-Map, add the argument `-wh http://127.0.0.1:4000` (with the host and port that the webhook is running on). You may also set this up in PokemonGo-Map's config.ini (just make sure you remove the hashtag and don't use quotations). 

7. If your PokeAlert process is receiving hits, you are all set! Go catch 'em all!
