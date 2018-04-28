# Standard Library Imports
# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_gmaps_link, get_applemaps_link, \
    get_dist_as_str, get_weather_emoji
from . import BaseEvent
from PokeAlarm import Unknown


class WeatherEvent(BaseEvent):
    """ Event representing the change occurred in Weather. """

    def __init__(self, data):
        """ Creates a new Weather Event based on the given dict. """
        super(WeatherEvent, self).__init__('weather')

        # Identification
        self.s2_cell_id = data.get('s2_cell_id')

        # Location
        self.lat = float(data['latitude'])  # To the center of the cell
        self.lng = float(data['longitude'])
        self.distance = Unknown.SMALL  # Completed by Manager
        self.direction = Unknown.TINY  # Completed by Manager

        # Weather Info
        self.weather_id = data.get('condition') or data.get('gameplay_weather')
        self.alert_id = data.get('alert_severity') or data.get('severity')
        self.day_or_night_id = data.get('day') or data.get('world_time')

        self.name = self.s2_cell_id
        self.geofence = Unknown.REGULAR
        self.custom_dts = {}

    def generate_dts(self, locale, timezone, units):
        """ Return a dict with all the DTS for this event. """
        weather_name = locale.get_weather_name(self.weather_id)
        alert_locale = locale.get_alert_name(self.alert_id)
        dts = self.custom_dts.copy()
        dts.update({
            # Identification
            's2_cell_id': self.s2_cell_id,

            # Location - center of the s2 cell
            'lat': self.lat,
            'lng': self.lng,
            'lat_5': "{:.5f}".format(self.lat),
            'lng_5': "{:.5f}".format(self.lng),
            'distance': (
                get_dist_as_str(self.distance, units)
                if Unknown.is_not(self.distance) else Unknown.SMALL),
            'direction': self.direction,
            'gmaps': get_gmaps_link(self.lat, self.lng),
            'applemaps': get_applemaps_link(self.lat, self.lng),
            'geofence': self.geofence,

            # Weather Info
            'weather_id': self.weather_id,
            'weather_id_3': "{:03}".format(self.weather_id),
            'weather': weather_name,
            'weather_emoji': get_weather_emoji(self.weather_id),
            'alert_id': self.alert_id,
            'alert_id_3': "{:03}".format(self.alert_id),
            'alert': alert_locale,
            'alert_or_empty': '' if self.alert_id is 0 else alert_locale,
            'day_or_night_id': self.day_or_night_id,
            'day_or_night_id_3': "{:03}".format(self.day_or_night_id),
            'day_or_night': locale.get_day_or_night(self.day_or_night_id)
        })
        return dts
