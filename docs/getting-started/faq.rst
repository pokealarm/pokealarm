FAQ
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:


General
-------------------------------------


Where should I go for support?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If, after *carefully* reading the Wiki and the rest of this FAQ, you can visit
our `Discord <https://discordapp.com/invite/S2BKC7p>`_. Make sure to read the
rules channel, so you don't inadvertently get banned.

Feel free to also open an issue on our
`Github <https://github.com/PokeAlarm/PokeAlarm/issues/new>`_ - just make sure
to use the correct template and to fill out all the information!


What Scanner should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We support a wide variety of scanners and forks - including Monocle,
Monocle-Alt, stock RocketMap, and RocketMap-Alt. PA relies on information from
Scanner via webhook - as a result, certain features may be available for some
scanners and not others.


How can I get request features?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Feel free to open an issue on our `Github`_ - just make sure to use the correct
template and to fill out all the information!

If your request is for a new service, use the
`New/Upcoming Services MEGA-THREAD <https://github.com/RocketMap/PokeAlarm/issues/147>`__
and mention you would like to see support for a certain service.

Discord is NOT a good place to request new features - it's highly likely your
request will be missed or ignored.


Do you accept Pull Requests?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yup! Feel free to open on against our `Github`_ - however it is a significant
change, it is probably best to consult us first.


How else can I support PA?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Besides submitting PRs or helping with the Wiki, Deadly (the original creator
and maintainer of PA) has a `Patreon <https://www.patreon.com/pokealarm>`_.


Startup Errors
-------------------------------------


PA throws a`ValueError` error about a JSON file?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First, make sure you haven't used Notepad or TextEdit on your configuration
files - they will disrupt the encoding on your file and cause issues.

Second, make sure your file is in the correct JSON format - Google "JSON
Formatting" and use a `JSON Editor https://www.jsoneditoronline.org/`__ to
verify you are in the right format.


Error about a 'Queue'?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PA only supports Python2, and not Python3.


ModuleNotFoundError: No module named X
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
After updating PA, make sure you always check for updated requirements.
Run the command ``pip install -r requirements.txt --upgrade`` from the PA
folder.


Runtime Errors
-------------------------------------

DTS reporting "Unknown"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you see a DTS being replaced by "?", "???", or "Unknown", that usually means
that your scanner didn't send enough information to PA for it to determine its
value. This could be


Gym Name DTS reporting "Unknown"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
RM doesn't do a good job of sending gym details through webhooks - to
make up for this, PA caches information between different webhooks. However
this cache takes a while to build up. You can also use the `file` cache to
prevent this cache


Why didn't I get an alert for this Event that is on my Map?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make sure that your filters are set up exactly as you want them - in
particular, make sure you understand the "is_missing_info" restriction. You
can use the webhook tester (``python tools/webhook_test.py``) to recreate an
event to verify they are working correctly.

Finally, check your scanner or PA for errors. If your scanner doesn't send the
info, PA can't process it.


Error 10053 (Windows) or Error 53 (Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This error means that PA tried to use a closed connection. It generally happens
when the server PA is running on it overloaded. Check your CPU and Disk IO - if
it is spiking when you get these errors, your server is under heavy load. There
some things you can still do:

+ If on Windows, use Linux (Even a VM will see huge improvements).
+ Run PA, your scanner, or your data base on separate servers if possible.
+ Optimize PA and your scanner setup.
+ Switch to a more efficient scanner (Monocle is typically harder to set up,
  but more efficient than RocketMap)
+ If all else fails, upgrade your hardware.


How can I optimize PA?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Generally, the biggest improvement you can see is to eliminate multiple
instances using managers. Managers can be consolidated by
using Rules. Lower the number of geofences you use, or the number of points
they contain. Finally, you can try to lower the number of filters you are
using.

Additionally, if you can set the 'concurrency' inside PA to a lower value -
this lowers the number of connections allowed to PA, which allows it to respond
faster.


How can I optimize my scanner?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the most part, you should consult the maintainer of your scanner for tips.
Generally, you want to follow the same logic and work towards consolidating
instances.

For RM in particular, there are default values you can adjust (particularly
around sending webhooks):
+ Disable extra webhooks - Use the blacklist/whitelist and disable types you
  don't need.
+ ``wh-lfu-size`` - (increase to 5000 or more) - this will increase RM's cache
  size and cause it to send less repeats.
+ ``wh-frame-interval`` - (increase up to 1000) - decreases the frequency in
  which RM sends events.
+ ``wh-backoff-factor`` - (increase .5 to 1)- if a connection does fail, this
  gives more time between retries.
+ ``wh-connect-timeout`` and ``wh-read-timeout`` - (PA recommends between 5 to
  10 seconds)- if you are experiencing periodic spikes of cpu or disk io, this
  gives your server more time to appropriately handle this request. Lowering
  this value could cause the connection to expire early, decreasing the chance
  of the webhook being delivered successfully and adding additional overhead
  from pipe errors and retries.
+ ``wh-threads`` and ``db-threads`` should be as low as possible (generally 1)
