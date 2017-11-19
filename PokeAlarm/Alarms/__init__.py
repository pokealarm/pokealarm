from Alarm import Alarm
from PokeAlarm.Utils import require_and_remove_key


def alarm_factory(settings, max_attempts, api_key):
    kind = require_and_remove_key('type', settings, "Alarm objects in Alarms file.")
    if kind == 'discord':
        from PokeAlarm.Alarms.Discord import DiscordAlarm
        return DiscordAlarm(settings, max_attempts, api_key)
    elif kind == 'facebook_page':
        from PokeAlarm.Alarms.FacebookPage import FacebookPageAlarm
        return FacebookPageAlarm(settings)
    elif kind == 'pushbullet':
        from PokeAlarm.Alarms.Pushbullet import PushbulletAlarm
        return PushbulletAlarm(settings)
    elif kind == 'slack':
        from PokeAlarm.Alarms.Slack import SlackAlarm
        return SlackAlarm(settings, api_key)
    elif kind == 'telegram':
        from PokeAlarm.Alarms.Telegram import TelegramAlarm
        return TelegramAlarm(settings)
    elif kind == 'twilio':
        from PokeAlarm.Alarms.Twilio import TwilioAlarm
        return TwilioAlarm(settings)
    elif kind == 'twitter':
        from PokeAlarm.Alarms.Twitter import TwitterAlarm
        return TwitterAlarm(settings)
    else:
        raise ValueError("%s is not a valid cache type!".format(kind))