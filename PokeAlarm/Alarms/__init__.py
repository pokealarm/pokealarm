from PokeAlarm.Utils import require_and_remove_key
from Alarm import Alarm  # noqa F401


def alarm_factory(mgr, settings, max_attempts, api_key):
    kind = require_and_remove_key(
        'type', settings, "Alarm objects in Alarms file.")
    if kind == 'discord':
        from PokeAlarm.Alarms.Discord import DiscordAlarm
        return DiscordAlarm(mgr, settings, max_attempts, api_key)
    elif kind == 'facebook_page':
        from PokeAlarm.Alarms.FacebookPage import FacebookPageAlarm
        return FacebookPageAlarm(mgr, settings)
    elif kind == 'pushbullet':
        from PokeAlarm.Alarms.Pushbullet import PushbulletAlarm
        return PushbulletAlarm(mgr, settings)
    elif kind == 'slack':
        from PokeAlarm.Alarms.Slack import SlackAlarm
        return SlackAlarm(mgr, settings, api_key)
    elif kind == 'telegram':
        from PokeAlarm.Alarms.Telegram import TelegramAlarm
        return TelegramAlarm(mgr, settings)
    elif kind == 'twilio':
        from PokeAlarm.Alarms.Twilio import TwilioAlarm
        return TwilioAlarm(mgr, settings)
    elif kind == 'twitter':
        from PokeAlarm.Alarms.Twitter import TwitterAlarm
        return TwitterAlarm(mgr, settings)
    else:
        raise ValueError("%s is not a valid alarm type!".format(kind))
