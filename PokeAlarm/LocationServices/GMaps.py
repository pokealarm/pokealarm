# Standard Library Imports
import collections
from datetime import datetime, timedelta
import logging
import time
import json
import traceback
# 3rd Party Imports
import requests
from requests.packages.urllib3.util.retry import Retry
from gevent.lock import Semaphore
# Local Imports
from PokeAlarm import Unknown
from PokeAlarm.Utilities.GenUtils import synchronize_with

log = logging.getLogger('Gmaps')


class GMaps(object):

    # Available travel modes for Distance Matrix calls
    TRAVEL_MODES = frozenset(['walking', 'biking', 'driving', 'transit'])

    # Maximum number of requests per second
    _queries_per_second = 50
    # How often to warn about going over query limit
    _warning_window = timedelta(minutes=1)

    def __init__(self, api_key):
        self._key = api_key
        self._lock = Semaphore

        # Create a session to handle connections
        self._session = self._create_session()

        # Sliding window for rate limiting
        self._window = collections.deque(maxlen=self._queries_per_second)
        self._time_limit = datetime.utcnow()

        # Memoization dicts
        self._geocode_hist = {}
        self._reverse_geocode_hist = {}
        self._dm_hist = {key: dict() for key in self.TRAVEL_MODES}

    # TODO: Move into utilities
    @staticmethod
    def _create_session(retry_count=3, pool_size=3, backoff=.25):
        """ Create a session to use connection pooling. """

        # Create a session for connection pooling and
        session = requests.Session()

        # Reattempt connection on these statuses
        status_forcelist = [500, 502, 503, 504]

        # Define a Retry object to handle failures
        retry_policy = Retry(
            total=retry_count,
            backoff_factor=backoff,
            status_forcelist=status_forcelist
        )

        # Define an Adapter, to limit pool and implement retry policy
        adapter = requests.adapters.HTTPAdapter(
            max_retries=retry_policy,
            pool_connections=pool_size,
            pool_maxsize=pool_size
        )

        # Apply Adapter for all HTTPS (no HTTP for you!)
        session.mount('https://', adapter)

        return session

    def _make_request(self, service, params=None):
        """ Make a request to the GMAPs API. """
        # Rate Limit - All APIs use the same quota
        if len(self._window) == self._queries_per_second:
            # Calculate elapsed time since start of window
            elapsed_time = time.time() - self._window[0]
            if elapsed_time < 1:
                # Sleep off the difference
                time.sleep(1 - elapsed_time)

        # Create the correct url
        url = u'https://maps.googleapis.com/maps/api/{}/json'.format(service)

        # Add in the API key
        if params is None:
            params = {}
        params['key'] = self._key

        # Use the session to send the request
        log.debug(u'{} request sending.'.format(service))
        self._window.append(time.time())
        request = self._session.get(url, params=params, timeout=3)

        if not request.ok:
            log.debug(u'Response body: {}'.format(
                json.dumps(request.json(), indent=4, sort_keys=True)))
            # Raise HTTPError
            request.raise_for_status()

        log.debug(u'{} request completed successfully with response {}.'
                  u''.format(service, request.status_code))
        body = request.json()
        if body['status'] == "OK" or body['status'] == "ZERO_RESULTS":
            return body
        elif body['status'] == "OVER_QUERY_LIMIT":
            # self._time_limit = datetime.utcnow() + _warning_window
            raise UserWarning(u'API Quota exceeded.')
        else:
            raise ValueError(u'Unexpected response status:\n {}'.format(body))

    @synchronize_with()
    def geocode(self, address, language='en'):
        # type: (str, str) -> tuple
        """ Returns 'lat,lng' associated with the name of the place. """
        # Check for memoized results
        address = address.lower()
        if address in self._geocode_hist:
            return self._geocode_hist[address]
        # Set default in case something happens
        latlng = None
        try:
            # Set parameters and make the request
            params = {'address': address, 'language': language}
            response = self._make_request('geocode', params)
            # Extract the results and format into a dict
            response = response.get('results', [])
            response = response[0] if len(response) > 0 else {}
            response = response.get('geometry', {})
            response = response.get('location', {})
            if 'lat' in response and 'lng' in response:
                latlng = float(response['lat']), float(response['lng'])

            # Memoize the results
            self._geocode_hist[address] = latlng
        except requests.exceptions.HTTPError as e:
            log.error(u"Geocode failed with "
                      u"HTTPError: {}".format(e.message))
        except requests.exceptions.Timeout as e:
            log.error(u"Geocode failed with "
                      u"connection issues: {}".format(e.message))
        except UserWarning:
            log.error(u"Geocode failed because of exceeded quota.")
        except Exception as e:
            log.error(u"Geocode failed because "
                      u"unexpected error has occurred: "
                      u"{} - {}".format(type(e).__name__, e.message))
            log.error(u"Stack trace: \n {}".format(traceback.format_exc()))
        # Send back tuple
        return latlng

    _reverse_geocode_defaults = {
        'street_num': Unknown.SMALL,
        'street': Unknown.REGULAR,
        'address': Unknown.REGULAR,
        'address_eu': Unknown.REGULAR,
        'postal': Unknown.REGULAR,
        'neighborhood': Unknown.REGULAR,
        'sublocality': Unknown.REGULAR,
        'city': Unknown.REGULAR,
        'county': Unknown.REGULAR,
        'state': Unknown.REGULAR,
        'country': Unknown.REGULAR
    }

    @synchronize_with()
    def reverse_geocode(self, latlng, language='en'):
        # type: (tuple) -> dict
        """ Returns the reverse geocode DTS associated with 'lat,lng'. """
        latlng = u'{:.5f},{:.5f}'.format(latlng[0], latlng[1])
        # Check for memoized results
        if latlng in self._reverse_geocode_hist:
            return self._reverse_geocode_hist[latlng]
        # Get defaults in case something happens
        dts = self._reverse_geocode_defaults.copy()
        try:
            # Set parameters and make the request
            params = {'latlng': latlng, 'language': language}
            response = self._make_request('geocode', params)
            # Extract the results and format into a dict
            response = response.get('results', [])
            response = response[0] if len(response) > 0 else {}
            details = {}
            for item in response.get('address_components'):
                for category in item['types']:
                    details[category] = item['short_name']

            # Note: for addresses on unnamed roads, EMPTY is preferred for
            # 'street_num' and 'street' to avoid DTS looking weird
            dts['street_num'] = details.get('street_number', Unknown.EMPTY)
            dts['street'] = details.get('route', Unknown.EMPTY)
            dts['address'] = u"{} {}".format(dts['street_num'], dts['street'])
            dts['address_eu'] = u"{} {}".format(
                dts['street'], dts['street_num'])  # Europeans are backwards
            dts['postal'] = details.get('postal_code', Unknown.REGULAR)
            dts['neighborhood'] = details.get('neighborhood', Unknown.REGULAR)
            dts['sublocality'] = details.get('sublocality', Unknown.REGULAR)
            dts['city'] = details.get(
                'locality', details.get('postal_town', Unknown.REGULAR))
            dts['county'] = details.get(
                'administrative_area_level_2', Unknown.REGULAR)
            dts['state'] = details.get(
                'administrative_area_level_1', Unknown.REGULAR)
            dts['country'] = details.get('country', Unknown.REGULAR)

            # Memoize the results
            self._reverse_geocode_hist[latlng] = dts
        except requests.exceptions.HTTPError as e:
            log.error(u"Reverse Geocode failed with "
                      u"HTTPError: {}".format(e.message))
        except requests.exceptions.Timeout as e:
            log.error(u"Reverse Geocode failed with "
                      u"connection issues: {}".format(e.message))
        except UserWarning:
            log.error(u"Reverse Geocode failed because of exceeded quota.")
        except Exception as e:
            log.error(u"Reverse Geocode failed because "
                      u"unexpected error has occurred: "
                      u"{} - {}".format(type(e).__name__, e.message))
            log.error(u"Stack trace: \n {}".format(traceback.format_exc()))
        # Send back dts
        return dts

    @synchronize_with()
    def distance_matrix(self, mode, origin, dest, lang, units):
        # Check for valid mode
        if mode not in self.TRAVEL_MODES:
            raise ValueError(u"DM doesn't support mode '{}'.".format(mode))
        # Estimate to about ~1 meter of accuracy
        origin = u'{:.5f},{:.5f}'.format(origin[0], origin[1])
        dest = u'{:.5f},{:.5f}'.format(dest[0], dest[1])

        # Check for memoized results
        key = origin + u':' + dest
        if key in self._dm_hist:
            return self._dm_hist[key]

        # Set defaults in case something happens
        dist_key = '{}_distance'.format(mode)
        dur_key = '{}_duration'.format(mode)
        dts = {dist_key: Unknown.REGULAR, dur_key: Unknown.REGULAR}
        try:
            # Set parameters and make the request
            params = {
                'mode': mode, 'origins': origin, 'destinations': dest,
                'language': lang, 'units': units
            }

            # Extract the results and format into a dict
            response = self._make_request('distancematrix', params)
            response = response.get('rows', [])
            response = response[0] if len(response) > 0 else {}
            response = response.get('elements', [])
            response = response[0] if len(response) > 0 else {}

            # Set the DTS
            dts[dist_key] = response.get(
                'distance', {}).get('text', Unknown.REGULAR)
            dts[dur_key] = response.get(
                'duration', {}).get('text', Unknown.REGULAR)
        except requests.exceptions.HTTPError as e:
            log.error(u"Distance Matrix failed with "
                      u"HTTPError: {}".format(e.message))
        except requests.exceptions.Timeout as e:
            log.error(u"Distance Matrix failed with "
                      u"connection issues: {}".format(e.message))
        except UserWarning:
            log.error(u"Distance Matrix failed because of exceeded quota.")
        except Exception as e:
            log.error(u"Distance Matrix failed because "
                      u"unexpected error has occurred: "
                      u"{} - {}".format(type(e).__name__, e.message))
            log.error(u"Stack trace: \n {}".format(traceback.format_exc()))
        # Send back DTS
        return dts
