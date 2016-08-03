import logging

from alarm import Alarm
from pushbullet import PushBullet, PushbulletError

log = logging.getLogger(__name__)

class Pushbullet_Alarm(Alarm):
	
	def __init__(self, settings):
		self.client = PushBullet(settings['api_key']) 
		log_msg = "Pushbullet Alarm intialized"
		if settings['channel']:
			try:
				self.channel = get_channel(self.client, settings['channel'])
                                log.info('Pushing to channel "' + settings['channel'] + '"')
			except PushbulletError:
				log.info('No channel found with channel_tag "' +
						settings['channel'] + '", pushing to all devices instead')
		if 'name' in settings:
			self.name = settings['name']
			log_mst = log_msg + ": " + self.name
		log.info(log_msg)
		push = self.client.push_note("PokeAlarm activated!", "We will alert you about pokemon.")
		
	def pokemon_alert(self, pkinfo):
		notification_text = pkinfo['alert']
		if hasattr(self, 'name') :
			notification_text = self.name + ": " + notification_text
		gmaps_link = pkinfo['gmaps_link']
		time_text =  pkinfo['time_text']
		if hasattr(self, 'channel'):
			push = self.channel.push_link(notification_text, gmaps_link, body=time_text)
		else:
			push = self.client.push_link(notification_text, gmaps_link, body=time_text)

def get_channel(client, channel_tag):
	req_channel = next((channel for channel in client.channels if channel.channel_tag == channel_tag), None)

	if req_channel is None:
		raise PushbulletError('No channel found with channel_tag "{}"'.format(channel_tag))

	return req_channel
