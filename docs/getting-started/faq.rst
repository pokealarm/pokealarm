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
rules channel carefully to avoid getting banned.

For bugs or support requests, feel free to also open an issue on our
`Github <https://github.com/PokeAlarm/PokeAlarm/issues/new>`_ - just make sure
to use the correct template and to fill out all the information!


What scanner should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We have support a wide variety of scanners and forks - including Monocle,
Monocle-Alt, Rocketmap-Stock, and RocketMap-Alt. PA relies on information from
your scanner via webhook - as a result, certain features may be supported by
certain scanners.


How can I get request features?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Feel free to open an issue on our `Github`_ - just make sure to use the correct
template and to fill out all the information!

Discord is NOT a good place to request new features - it's highly likely your
request will be missed or ignored. If you want to make sure you get a response,
please use the Github page.


Do you accept Pull Requests?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yup! Feel free to open one against our `Github`_ - if is a significant change,
it is probably best to consult the team before sinking too much time in.


How else can I support PA?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Besides submitting PRs or helping with the Wiki, you can support Deadly (the
original creator and maintainer of PA) via
`Patreon <https://www.patreon.com/pokealarm>`_.
To buy someone on the team a drink, use the ``!support`` command in the PA
Discord for the relevant links.


Startup Errors
-------------------------------------


PA throws a`ValueError` error about a JSON file?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
First, make sure you haven't used Notepad or TextEdit on your configuration
files - they change the encoding on your file and cause issues.

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

Additionally, ensure you are using Python2 and pip2 instead of Python3
utilities.


Runtime Errors
-------------------------------------

DTS reporting "Unknown"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you see a DTS being replaced by "?", "???", or "Unknown", that usually means
that your scanner didn't send enough information to PA for it to determine its
value. This is usually one of two reasons - the scanner might not know
the value, or else it doesn't support the DTS.

Gym Name DTS reporting "Unknown"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Some scanners (Stock-RM in particular) do not send relevant gym details through
each webhook - to compensate up for this, PA caches information between
different webhooks. However this cache can take a while to build up. You can
also use the ``file`` cache, which will save and load it's contents to a file
in between runtimes.


Why didn't I get an alert for this Event that is on my Map?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make sure that your filters are set up exactly as you want them - in
particular, make sure you understand the "is_missing_info" restriction. You
can use the webhook tester (``python tools/webhook_test.py``) to recreate an
event to verify they are working correctly.

Finally, check your both PA and your scanner for any errors related to
webhooks. If your scanner doesn't send the info, PA can't process it.


Error 10053 (Windows) or Error 53 (Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. warning::

    The PA team has identified a number of issues with RM's webhook handling
    that can lead to an overloaded web server and dropped connections. Since
    these problems mean a significant chance of dropped or missed events, the
    PA team has created repos with fixes applied under our Github org - you can
    find them at PokeAlarm/RM-Stock and PokeAlarm//RM-Alt.

This error means that PA tried to use a connection that has already been
closed. It often happens when the server PA is running on is overloaded. Check
your CPU and Disk IO - if it is spiking when you get these errors, your server
is under heavy load. There some things you can still do:

+ If on Windows, use Linux (Even a VM will see huge improvements).
+ Optimize PA and your scanner setup (see below).
+ Switch to a more efficient scanner (While Monocle is typically harder to set
  up, it is significantly more efficient than RocketMap)
+ Run PA, your scanner, or your database on separate machines if possible.
+ If all else fails, upgrade your hardware.


How can I optimize PA?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In terms of efficiency Rules are better than Managers, and Managers
are better than instances. As such, reducing the number of instances by using
Managers and reducing the number of Managers by using Rules.

This holds true with one caveat - due to limitations with the Python GIL, each
PA process is limited to a single processor core. If you wish to take advantage
of multiple cores, running instances may increase your throughput. Do **not**
follow any advice to use a load balancer - PA is a stateful application, and
this will cause problems. Instead, pair instances of your scanner with
instances of PA that make logical sense.

Finally, you can lower the 'concurrency' setting for PA to a lower value -
this limits the number of connections PA can handle at once. Lowering this
value will reduce overhead and increase response times.

If you need additional advice, feel free to ask in our Discord.

How can I optimize my scanner?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For the most part, you should consult the maintainer of your scanner for tips.
Generally, you want to follow the same logic and work towards consolidating
instances.

.. warning::

    The PA team has identified a number of issues with RM's webhook handling
    that can lead to an overloaded web server and dropped connections. Since
    these problems mean a significant chance of dropped or missed events, the
    PA team is hosting repos with fixes applied under our Github org - you can
    find them at PokeAlarm/RM-Stock and PokeAlarm//RM-Alt.

For RM in particular, there are default values you can adjust (particularly
around sending webhooks):
+ Disable extra webhooks - Use the blacklist/whitelist and disable types you
  don't need.
+ ``wh-frame-interval`` - (increase to 1000) - decreases the frequency in
  which RM sends events. There is currently a bug in RM flavor maps that make
  setting this below 1000 equivalent to disabling it.
+ ``wh-connect-timeout`` and ``wh-read-timeout`` - (PA recommends between 5 to
  10 seconds). Increasing the timeouts allows for more robust connections and
  decrease issues you may encounter with latency, transient network errors, or
  periodic spikes of cpu or disk io. Do **NOT** follow advice to lower this
  value below the default - lowering this value increases the chance of a
  connection expiring early due to the above reasons, which can lead to dropped
  or missed events.
+ ``wh-lfu-size`` - (increase to 10000 or more) - this will increase RM's cache
  size and cause it to send less repeats. The ideal value for this is roughly
  around the number of events you scan in an hour.
+ ``wh-backoff-factor`` - (increase to .5 to 1)- if a connection does fail,
  this gives more time between retries.
+ ``wh-threads`` and ``db-threads`` should be as low as possible (generally 1)
