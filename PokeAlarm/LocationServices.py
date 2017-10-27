# Standard Library Imports
import logging
import traceback
# 3rd Party Imports
import googlemaps
# Local Imports

log = logging.getLogger('LocService')


# Class to handle Location Services
class LocationService(object):

    # Initialize the APIs
    def __init__(self, api_key, locale, units):
        self.__client = googlemaps.Client(key=api_key, timeout=3, retry_timeout=5)

        self.__locale = locale # Language to use for Geocoding results
        self.__units = units # imperial or metric

        # For Reverse Location API
        self.__reverse_location = False
        self.__reverse_location_history = {}
        # Walking Dist/Time
        self.__walk_data = False
        self.__walk_data_history = {}
        # Bike Dist/Time
        self.__biking_data = False
        self.__bike_data_history = {}
        # Drive Dist/Time
        self.__driving_data = False
        self.__driving_data_history = {}

    # Add any API-dependant DTS as required
    def add_optional_arguments(self, origin, dest, dict):
        if self.__reverse_location:
            dict.update(**self.__get_reverse_location(dest))
        if self.__walk_data:
            dict.update(**self.__get_walking_data(origin, dest))
        if self.__biking_data:
            dict.update(**self.__get_biking_data(origin, dest))
        if self.__driving_data:
            dict.update(**self.__get_driving_data(origin, dest))

    # Returns an array in the format [ Lat, Lng ]. Will exit if an error occurs.
    def get_location_from_name(self, location_name):
        try:
            result = self.__client.geocode(location_name, language=self.__locale)
            loc = result[0]['geometry']['location']  # Get the first (most likely) result
            latitude, longitude = loc.get("lat"), loc.get("lng")
            log.debug("Coordinates found for name '{}': {:f},{:f}".format(location_name, latitude, longitude))
            return [latitude, longitude]
        except Exception as e:
            log.error("Encountered error attempting to receive location from name{}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return None

    # Enable the Reverse Location call in optional arguments
    def enable_reverse_location(self):
        if not self.__reverse_location:
            self.__reverse_location = True
            log.info("Reverse Location DTS detected - API has been enabled!")

    # Returns details about a location from coordinates in the [Lat, Lng] format
    def __get_reverse_location(self, location):
        # Memoize the results
        key = "{:.5f},{:.5f}".format(location[0], location[1]) # ~1 meter of precision
        if key in self.__reverse_location_history:
            return self.__reverse_location_history[key]

        details = { # Set some defaults in case something goes wrong
            'street_num': '???', 'street': 'unknown', 'address': 'unknown', 'postal': 'unknown',
            'neighborhood': 'unknown', 'sublocality': 'unknown', 'city': 'unknown',
            'county': 'unknown', 'state': 'unknown', 'country': 'country'
        }
        try:
            result = self.__client.reverse_geocode(location, language=self.__locale)[0]
            loc = {}
            for item in result['address_components']:
                for category in item['types']:
                    loc[category] = item['short_name']
            details['street_num'] = loc.get('street_number', '???')
            details['street'] = loc.get('route', 'unknown')
            details['address'] = "{} {}".format(details['street_num'], details['street'])
            details['postal'] = loc.get('postal_code', 'unknown')
            details['neighborhood'] = loc.get('neighborhood', "unknown")
            details['sublocality'] = loc.get('sublocality', "unknown")
            details['city'] = loc.get('locality', loc.get('postal_town', 'unknown'))
            details['county'] = loc.get('administrative_area_level_2', 'unknown')
            details['state'] = loc.get('administrative_area_level_1', 'unknown')
            details['country'] = loc.get('country', 'unknown')
            self.__reverse_location_history[key] = details # If everything was successful, memoize for next time
        except Exception as e:
            log.error("Encountered error while getting reverse location data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        # Return results, even if unable to complete
        return details

    # Enable the Walking Distance Matrix call in optional arguments
    def enable_walking_data(self):
        if not self.__walk_data:
            self.__walk_data = True
            log.info("Walking Data DTS detected - API has been enabled!")

    # Returns a set with walking dist and walking duration via Google Distance Matrix API
    def __get_walking_data(self, origin,  dest):
        origin = "{:.5f},{:.5f}".format(origin[0], dest[1])
        dest = "{:.5f},{:.5f}".format(dest[0], dest[1])
        key = origin + "to" + dest
        if key in self.__walk_data_history:
            return self.__walk_data_history[key]
        data = {'walk_dist': "unknown", 'walk_time': "unknown"}
        try:
            result = self.__client.distance_matrix(origin, dest,
                                                        mode='walking', units=self.__units, language=self.__locale)
            result = result.get('rows')[0].get('elements')[0]
            data['walk_dist'] = result.get('distance').get('text').encode('utf-8')
            data['walk_time'] = result.get('duration').get('text').encode('utf-8')
            self.__walk_data_history[key] = data
        except Exception as e:
            log.error("Encountered error while getting walking data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    # Enable the Biking Distance Matrix call in optional arguments
    def enable_biking_data(self):
        if not self.__biking_data:
            self.__biking_data = True
            log.info("Biking Data DTS detected - API has been enabled!")

    # Returns a set with biking dist and biking duration via Google Distance Matrix API
    def __get_biking_data(self, origin,  dest):
        origin = "{:.5f},{:.5f}".format(origin[0], dest[1])
        dest = "{:.5f},{:.5f}".format(dest[0], dest[1])
        key = origin + "to" + dest
        if key in self.__bike_data_history:
            return self.__bike_data_history[key]
        data = {'bike_dist': "unknown", 'bike_time': "unknown"}
        try:
            result = self.__client.distance_matrix(origin, dest,
                                                        mode='bicycling', units=self.__units, language=self.__locale)
            result = result.get('rows')[0].get('elements')[0]
            data['bike_dist'] = result.get('distance').get('text').encode('utf-8')
            data['bike_time'] = result.get('duration').get('text').encode('utf-8')
            self.__bike_data_history[key] = data
        except Exception as e:
            log.error("Encountered error while getting biking data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

    # Enable the Biking Distance Matrix call in optional arguments
    def enable_driving_data(self):
        if not self.__driving_data:
            self.__driving_data = True
            log.info("Driving Data DTS detected - API has been enabled!")

    # Returns a set with driving dist and biking duration via Google Distance Matrix API
    def __get_driving_data(self, origin,  dest):
        origin = "{:.5f},{:.5f}".format(origin[0], dest[1])
        dest = "{:.5f},{:.5f}".format(dest[0], dest[1])
        key = origin + "to" + dest
        if key in self.__driving_data_history:
            return self.__driving_data_history[key]
        data = {'drive_dist': "unknown", 'drive_time': "unknown"}
        try:
            result = self.__client.distance_matrix(origin, dest,
                                                        mode='driving', units=self.__units, language=self.__locale)
            result = result.get('rows')[0].get('elements')[0]
            data['drive_dist'] = result.get('distance').get('text').encode('utf-8')
            data['drive_time'] = result.get('duration').get('text').encode('utf-8')
            self.__driving_data_history[key] = data
        except Exception as e:
            log.error("Encountered error while getting driving data ({}: {})".format(type(e).__name__, e))
            log.debug("Stack trace: \n {}".format(traceback.format_exc()))
        return data

