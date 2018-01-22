# Standard Library Imports
# 3rd Party Imports
# Local Imports
from . import BaseFilter


class WeatherFilter(BaseFilter):
    """ Filter class for limiting which egg trigger a notification. """

    def __init__(self, name, data):
        """ Initializes base parameters for a filter. """
        super(WeatherFilter, self).__init__(name)

        # Geofences
        self.geofences = BaseFilter.parse_as_set(str, 'geofences', data)

        # Custom DTS
        self.custom_dts = BaseFilter.parse_as_dict(
            str, str, 'custom_dts', data)

        # Missing Info
        self.is_missing_info = BaseFilter.parse_as_type(
            bool, 'is_missing_info', data)

        # Reject leftover parameters
        for key in data:
            raise ValueError("'{}' is not a recognized parameter for"
                             " Weather filters".format(key))

    def to_dict(self):
        """ Create a dict representation of this Filter. """
        settings = {}

        # Geofences
        if self.geofences is not None:
            settings['geofences'] = self.geofences

        # Missing Info
        if self.is_missing_info is not None:
            settings['missing_info'] = self.is_missing_info

        return settings
