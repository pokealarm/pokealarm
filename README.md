# PokeAlarm

PokeAlarm is a third party extension for [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) that allows you to receive external notifications via the service of your choice.

We currently support Pushbullet, Slacker, Twilio (SMS), and Telegram. Pushbullet support will likely be dicontinued after August 1st (because I am a poor college student). 

If you are experiencing issues with the alarm or would like to see new features, please open a ticket here on github. 

If you are experiencing trouble with setup or other user difficulties, please see the reddit thread.

## Common Problems

### Windows: socket.error: [Errno 10053] An established connection was aborted by the software in your host machine OR Linux: socket.error: [Errno 32] Broken pipe

This problem is an issue with the PokemonGo-Map. The Map sends the POST request but does not leave proper time for the server to respond. Because of the setup of Flask, this error seems to be impossible for me to fix. You can either make a pull of my fixed version [here](https://github.com/kvangent/PokemonGo-Map/tree/time_fix) or you can apply the following changes yourself: 

Go to PokemonGo-Map/pgom/utils.py and find the line `requests.post(w, json=data, timeout=(None, 1))`. Change to `requests.post(w, json=data, timeout=(None, 5))`. If you still experience the problem with 5, try to up it to 10. This should fix the problem for you.

### Problems with receiving in UTC time or Notifications not sending because time_left has passed.

This is a problem with the PokemonGo-Map sending an object with UTC time listed as a native time object. I have corrected the mistake in my fork [here](https://github.com/kvangent/PokemonGo-Map/tree/time_fix) or you can apply the following changes yourself: 

1. Change the line (4-5) 'import time' to `import calendar`. 
2. Change the line (269ish) `'disappear_time': time.mktime(d_t.timetuple()).` to `'disappear_time': calendar.timegm(d_t.timetuple())`

## Setup

1. Setup and run [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) to make sure you have everything working.

2. Clone a local copy of PokeAlarm (`git clone https://github.com/kvangent/PokeAlarm`) and navigate inside the folder.

3. Run pip to install requirements `pip install -r requirements.txt`

4. Copy alarms.json.default and rename it to alarms.json. Edit the file (Windows Users: NOT with notepad) with your configuration settings. Make sure to change the pokemon you want to be alerted to "True". Each alarm configuration will be added to the wiki shortly. All the fields are required except for the 'name' field - it can be left blank or not included in the config at all. You can also add multple of the same alarm type.

5. Start the webhook server with `python runwebhook.py`. You should receive a notification if your alarm is set up correctly. You can specify a host and port with `-H HOST -P PORT`. The default is a host of 127.0.0.1 and port of 4000. This is the port that the webhook will listen on. The port number MUST be different to what you run your PokemonGo-Map server on!

6. When you start the PokemonGo-Map, add the argument `-wh http://127.0.0.1:4000` (with the host and port that the webhook is running on). You may also set this up in PokemonGo-Map's config.ini (just make sure you remove the hashtag and don't use quotations). 

7. If your PokeAlert process is receiving hits, you are all set! Go catch 'em all!

## FAQ

Q. Which version of PokemonGo-Map do I need?
A. Either dev or master, both have included webhook support. This program is an extension, so we can update one without affecting the other. The master branch is more stable, so I would recommend that. 

Q. Will you be adding support for XXX?
A. Open a ticket with a link to the service API you are interested in and I will see what I can do.

Q. Man I wish this could do XXX!
A. Open an issue request and I will look into it. (Or do it yourself and open a pull request)

Q. I am receiving XXX error from PokemonGo-Map! What do?
A. Checkout the [PokemonGo-Map Wiki](https://github.com/PokemonGoMap/PokemonGo-Map/wiki) or the reddit thread to see if anyone has any suggestions for you.

Q. I am receiving error about JSON input from PokeAlarm?
A. If you are a Windows user, stop using notepad and start using Notepad++. Make a fresh copy of the alarms.json and remake your changes. If you aren't a Windows user (or you are already using Notepad++) check your JSON format with a JSON formatter for issues.