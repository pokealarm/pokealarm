# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from . import BaseEvent
from PokeAlarm.Utils import get_time_as_str 
   

class WeatherEvent(BaseEvent):
    """ Event representing the change occurred in Weather """

    def __init__(self, data):
        """ Creates a new Weather Event based on the given dict. """
        super(WeatherEvent, self).__init__('weather')
        check_for_none = BaseEvent.check_for_none

        # Identification
        self.alert_type = 'weather'
        self.weather_cell_id = data.get('s2_cell_id')

        #Time of weather change
        self.time_changed = datetime.utcfromtimestamp(
            data.get('time_changed'))

        #S2 Cell vertices coordinates
        self.coords = data.get('coords')

        #Weather conditions
        self.condition = check_for_none(
            int, data.get('condition'), Unknown.SMALL)
        self.alert_severity = check_for_none(
            str, data.get('alert_severity'), Unknown.SMALL)
        self.warn = check_for_none(
            str, data.get('warn'), Unknown.REGULAR).strip()
        self.day = check_for_none(
            int, data.get('day'), Unknown.SMALL)

        self.name = self.weather_cell_id
        self.manager = ''
        self.custom_dts = {}

    def generate_dts(self, locale):
        """ Return a dict with all the DTS for this event. """
        time_changed = get_time_as_str(self.time_changed)
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            'alert_type': self.alert_type,
            'weather_cell_id': self.weather_cell_id,

            # Time Remaining
            '12h_time_weather_changed': time_changed[1],
            '24h_time_weather_changed': time_changed[2],

            # Location
            'coords': self.coords,

            'geofence': self.geofence,
            'manager': self.manager,
            
            # Weather info
            'condition': self.condition,
            'weather': locale.get_weather_name(self.condition),
            'alert_severity': self.alert_severity,
            'warn': self.warn,
            'day': self.day
        })
        return dts
