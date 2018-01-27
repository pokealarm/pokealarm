# FAQ

## Overview
* [General Info](#general-info)
* [Troubleshooting](#troubleshooting)

## General Info

These are general questions about PA and it's development.

#### Where should I go for support?
* If, after *carefully* reading the Wiki and the rest of this FAQ, you
can visit our [Discord](https://discordapp.com/invite/S2BKC7p). Make
sure to read the rules channel, so you don't inadvertently get banned.

#### What scanners are supported?
* Currently RocketMap (RM) and Monocle are compatible with PA.
If you are interested in adding support for your program, feel free to
read the [Webhook Standards](webhook-standard) and ask us in Discord
what you can do to add support for PA.

#### I have a great idea for a new feature!
* Open a Feature Request on our Github page. Use the
[correct template](https://github.com/PokeAlarm/PokeAlarm/issues/new)
- Please **DO NOT** just ask for a feature in Discord. There is a lot of
chat in discord and your request will certainly get lost. Issues let us
track the request and real with it in a more concrete manor.
- If you see a request you like, be sure to comment on it to show your
support!


#### Do you accept PRs?
* Yup - you can submit them via Github. If it is a big change, feel free
to approach us before so we can coordinate better.

#### Do you support new services?
* Please check in the
[New/Upcoming Services MEGA-THREAD](https://github.com/RocketMap/PokeAlarm/issues/147)
to see if the service has already been requested. If it hasn't, feel
free to leave a post requesting it.

#### How can I support PokeAlarm?
* Besides submitting PRs or helping us with the
[Wiki](https://github.com/PokeAlarm/PokeAlarmWiki), you can support
Deadly (the creator of PA) on
[Patreon](https://www.patreon.com/pokealarm).


## Troubleshooting

#### PokeAlarm complains about a `ValueError` error and says I need to talk to some guy named JSON?
1. Make sure you didn't open any files with Notepad or TextEdit - they
can break the encoding on your files. Use Notepad++ or a better editor.
2. If you sure that isn't the problem, then you probably have an error
with your JSON Formatting. Look up how JSON formatting works and use a
[JSON Editor](http://www.jsoneditoronline.org/) to find your problem.

#### Why isn't `<gym_name>` working right?
* You must have gym-details enabled in your scanner and webhook options.
* Most scanners don't send the gym-details with every gym related
webhook - PA will cache the details and try to remember them, but
this goes away upon restart. It takes time for the scanner to send all
the details.

You can use file-caching to save the gym names to a file so that they
are available upon restart. Check out the
[Object Caching](object-caching) page for more information.

#### How can I optimize PokeAlarm?
PA uses Gevent and Multiprocessing to be as responsive as possible to
incoming requests. However (due to language and hardware limitations),
it is possible for PA to be overwhelmed and have a hard time handling
requests for large setups. If you are experiencing problems, you can try
the following options:
1. If on Windows, try Linux (even a VM will see large improvements).
2. Run PA on a separate server.
3. Lower the number of managers you are using. Each manager runs in its
own process, which makes it expensive.
4. If possible, separate scanners and pa instances into smaller groups
and even onto different servers.
5. Upgrade your server hardware.

PA also has a `concurrency` setting that can be lowered - it limits the
number of active connections allowed to it. This will prevent PA

Additionally, there are a number of settings in RM to optimize:
1. Disable extra webhooks - use RM's blacklist/whitelist and disable
webhook types you aren't using.
2. Lower webhook-threads (`wh-concurrent` or similar) - This will cause
RM to send less connections at once.
3. Increase `wh-frame-interval` - Increase the number of events RM sends
at once to lower overhead.
5. Increase `wh-lfu-size` - this will increase RM's cache size to repeat
less information.
6. Increase `wh-backoff-factor` - Increase break between webhooks.
7. Increase `wh-connect-timeout` and `#wh-read-timeout` timeouts for RM.
This gives your server more time to react.
8. Decrease database threads `db-concurrency` or similar - uses less
sockets.
**Note:** Decreasing/Increase these settings may cause queue build up
in a variety of different places. It is a matter of trial and error to
find the ideal settings for your setup.

Try the RM (or PA) discord for more info.


#### Error 10053 on Windows or Error 53 on Linux?
* This is an issue with too many open sockets on windows that causes
PA to be unable to open an new connections. See the above steps for
some suggestions on optimization.


#### RocketMap repeatedly spams `Caused by ReadTimeoutError("HTTPConnectionPool(host='127.0.0.1', port=4000)`?
* This mean's that RM is not connecting to PA for some reason:
1. Make sure PA is running.
2. Make sure RM is sending to the correct IP:PORT combo.
3. If the PokeAlarm instance is on a remote server, try increasing RM's
`wh-timeout` parameter (which defaults to 1s).
4. Check hardware for a bottleneck. See above for optimizations.

#### Why do some DTS (`<iv>`, etc) or another DTS show up as `?`?
* PA replaces DTS that are used with `?`, `???`, or `unknown` when it
doesn't know the correct information. This could be a variety of reasons

#### Map images aren't showing up correctly... What can I do?
* Make sure you have added a [Google API Key](google-maps-api-key) and
have the Static Maps API enabled. If you already have it enabled, make
sure that you haven't hit the limit for free users.

#### Missing icons in your alerts?
* Remove your lines from `icon_url` and `avatar_url` from your
[Alarms](alarms) to use the default images in the PA.

#### Do you want to use custom images in your alerts?
* Add in your alarms the option to add images (depends on the service
that is used) and add your url where the images are. For example, if you
use [Discord](discord) it will be something like this:

```
"icon_url":"https://raw.githubusercontent.com/user/PokeIcons/master/icons/<pkmn_id>.png"
```
