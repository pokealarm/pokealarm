#Setup Logging
import logging
log = logging.getLogger(__name__)

#Local modules
from ..alarm import Alarm
from ..utils import *
#Bot Implementation Requirements
import requests
from json import dumps as jsondumps


class Groupme_Alarm(Alarm):
  # notice: groupme does NOT support percent signs (%) in the message.
  # I do not know how to fix this. Somebody fix this.
  _defaults = {
  'pokemon':{
  'location_name':"<pkmn> until <24h_time>",
      'text':"<pkmn> here until <24h_time> (<time_left>).\n IV: <atk>/<dfs>/<sta> \n Move 1: <move1> \n Move 2: <move2>"
    },
    'pokestop':{
      'location_name':"Lured Pokestop",
      'text':"A pokestop has been lured. Lure will expire at <24h_time> (<time_left>)."
    },
    'gym':{
      'location_name':"Recently fallend gym",
      'text':"A Team <old_team> gym has fallen and is now controlled by <new_team>"
    }
  }

  #Gather settings and create alarm
  def __init__(self, settings):
    self.bot_id = settings.get('bot_id')
    self.group_id = settings.get('group_id')
    #Set Alerts
    self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
    self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
    self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
    log.info('Groupme Bot Sending')

  #(Re)establishes Service connection
  def connect(self):
    log.info('Groupme bot connected (even though it doesnt really need to connect)')

  #Set the appropriate settings for each alert
  def set_alert(self, settings, default):
    alert={
           'location_name': settings.get('location_name', default['location_name']),
           'text' : settings.get('text' , default['text']),
          }
    return alert

  #Send Alert to the Service
  def send_alert(self, alert_settings, info):
    args = {
      'location_name': replace(alert_settings['location_name'], info),
      'text'         : replace(alert_settings['text']         , info),
      'latitude'     : info['lat'],
      'longitude'    : info['lng']
    }
    try_sending(log, self.connect, "Groupme", self.send_groupme, args)

  #Trigger an alert based on Pokemon info
  def pokemon_alert(self, pokemon_info):
    self.send_alert(self.pokemon, pokemon_info)
  #Trigger an alert based on PokeLure info
  def pokestop_alert(self, pokestop_info):
    self.send_alert(self.pokestop, pokestop_info)
  #Trigger an alert based on PokeGym info
  def gym_alert(self, gym_info):
    self.send_alert(self.gym, gym_info)

  # send groupme
  def send_groupme(self, location_name='N/A', text='N/A', latitude=0, longitude=0):
    data = {'bot_id'  :self.bot_id,
            'group_id':self.group_id,
            'text'    :text,
            'attachments':
            [
              {'type':'location',
               'lng' :longitude,
               'lat' :latitude,
               'name':location_name
              }
            ]
           }
    log.debug('Groupmebot preporing to send data:', data)
    r = requests.post('https://api.groupme.com/v3/bots/post', jsondumps(data))
    r.raise_for_status()
