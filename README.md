# Fork of PokeAlarm with support for hardware with blynk

PokeAlarm is a third party extension for [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) that allows you to receive external notifications via the service or hardware of your choice.

The following services are currently supported in this fork:
* Pushbullet
* Pushover
* Slacker
* Telegram 
* Twilio (SMS)
* blynk/ Hardware (proof of concept; still much to fix)

## Basic Setup

1. Setup and run [PokemonGo-Map](https://github.com/PokemonGoMap/PokemonGo-Map) to make sure you have everything working.

2. Clone a local copy of PokeAlarm (`git clone https://github.com/kvangent/PokeAlarm`) and navigate inside the folder.

3. Run pip to install requirements `pip install -r requirements.txt`

4. Copy alarms.json.default and rename it to alarms.json. Edit the file (Windows Users: NOT with notepad) with your configuration settings. Make sure to change the pokemon you want to be alerted to "True". Each alarm configuration will be added to the wiki shortly. All the fields are required except for the 'name' field - it can be left blank or not included in the config at all. You can also add multple of the same alarm type.  You can specify a different configuration file with `-cn <config_file.json>`.

5. Start the webhook server with `python runwebhook.py`. You should receive a notification if your alarm is set up correctly. You can specify a host and port with `-H HOST -P PORT`. The default is a host of 127.0.0.1 and port of 4000. This is the port that the webhook will listen on. The port number MUST be different to what you run your PokemonGo-Map server on!

6. When you start the PokemonGo-Map, add the argument `-wh http://127.0.0.1:4000` (with the host and port that the webhook is running on). You may also set this up in PokemonGo-Map's config.ini (just make sure you remove the hashtag and don't use quotations). 

7. If your PokeAlert process is receiving hits, you are all set! Go catch 'em all!



##Optional additional Setup for Hardware blynk Device
For images of the device and the working process look in the wiki

###Hardware Needed:
1. ESP8266 (best use ESP8266 dev boards with usb like wemos d1 mini or nodemcu)
2. pushbutton or touch button
3. [SparkFun Micro OLED Breakout](https://www.sparkfun.com/products/13003) or if you use a wemos 1 mini you could use the oled shield like I did
(other oleds screen should work to but require some knowledge and adjustment to the code and librarys used)

### setup of hardware and plugins

1. Open up your blynk app for ios/android and create a new project. As hardware set ESP8266 and send the api key to your email adress.

2. Edit your `alarms.json`, set blynk to true, put in the Blynk api Key you sent to your Email, optionally edit the search radius you desire (tipps for this in the `alarms.json.editors_choice`) and don't forget to set some Pokemon to true, but not too many so your Hardware won't overflows.

3. You need to install two libraries into the Arduino IDE first you need the [Blynk Arduino library](http://www.blynk.cc/getting-started/) and then you need a [modified version of the sparkfun oled library](https://github.com/EdwinRobotics/ER_Micro_OLED_Arduino_Library)

4. Connect your ESP8266 per usb serial com device or esp8266 development boards (like the by wemos d1 mini used by me) to load the Arduino sketch onto the hardware.
   
5. Don't forget to put in your WIFI credentials, your previously retrieved blynk api key and your pushbullet api key at the beginning of the sketch.

6. Connect a push button to the Pin defined in the arduino sketch.

7. Set up a Web server with php activated (there are many tutorials out there for apache2 or lighttpd) and copy the `gps.php` and `gps.txt` to `/var/www/html`. Change the permissions of` gps.txt` to owner modify, group and user read and on a command line `sudo chown www-data:www-data gps.txt`    

8. Install the gps logger app for android (https://play.google.com/store/apps/details?id=com.mendhak.gpslogger) or any app, that can send your gps to `http://YOURSERVER/gps.php?lat=%LAT&long=%LON`

9. On your phone set up a Mobile Hotspot with the SSID and password you defined in the Arduino sketch
