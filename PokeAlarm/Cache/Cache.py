# Standard Library Imports
from datetime import datetime
# 3rd Party Imports
# Local Imports
from PokeAlarm import Unknown
from PokeAlarm.Utils import get_image_url


class Cache(object):
    """ Basic object for caching information.

    This object caches and manages information in Memory. Information will
    be lost between run times if save has not been implemented correctly.
    """

    default_image_url = get_image_url("regular/gyms/0.png"),

    def __init__(self, mgr):
        """ Initializes a new cache object for storing data between events. """
        self._log = mgr.get_child_logger("cache")

        self._mon_hist = {}
        self._stop_hist = {}
        self._egg_hist = {}
        self._raid_hist = {}
        self._gym_team = {}
        self._gym_name = {}
        self._gym_desc = {}
        self._gym_image = {}
        self._cell_weather_id = {}
        self._severity_id = {}
        self._day_or_night_id = {}

    def monster_expiration(self, mon_id, expiration=None):
        """ Update and return the datetime that a monster expires."""
        if expiration is not None:
            self._mon_hist[mon_id] = expiration
        return self._mon_hist.get(mon_id)

    def stop_expiration(self, stop_id, expiration=None):
        """ Update and return the datetime that a stop expires."""
        if expiration is not None:
            self._stop_hist[stop_id] = expiration
        return self._stop_hist.get(stop_id)

    def egg_expiration(self, egg_id, expiration=None):
        """ Update and return the datetime that an egg expires."""
        if expiration is not None:
            self._egg_hist[egg_id] = expiration
        return self._egg_hist.get(egg_id)

    def raid_expiration(self, raid_id, expiration=None):
        """ Update and return the datetime that a raid expires."""
        if expiration is not None:
            self._raid_hist[raid_id] = expiration
        return self._raid_hist.get(raid_id)

    def gym_team(self, gym_id, team_id=Unknown.TINY):
        """ Update and return the team_id of a gym. """
        if Unknown.is_not(team_id):
            self._gym_team[gym_id] = team_id
        return self._gym_team.get(gym_id, Unknown.TINY)

    def gym_name(self, gym_id, gym_name=Unknown.REGULAR):
        """ Update and return the gym_name for a gym. """
        if Unknown.is_not(gym_name):
            self._gym_name[gym_id] = gym_name
        return self._gym_name.get(gym_id, Unknown.REGULAR)

    def gym_desc(self, gym_id, gym_desc=Unknown.REGULAR):
        """ Update and return the gym_desc for a gym. """
        if Unknown.is_not(gym_desc):
            self._gym_desc[gym_id] = gym_desc
        return self._gym_desc.get(gym_id, Unknown.REGULAR)

    def gym_image(self, gym_id, gym_image=Unknown.REGULAR):
        """ Update and return the gym_image for a gym. """
        if Unknown.is_not(gym_image):
            self._gym_image[gym_id] = gym_image
        return self._gym_image.get(gym_id, get_image_url('icons/gym_0.png'))

    def cell_weather_id(self, s2_cell_id, cell_weather_id=Unknown.REGULAR):
        """ Update and return weather_id for a cell """
        if Unknown.is_not(cell_weather_id):
            self._cell_weather_id[s2_cell_id] = cell_weather_id
        return self._cell_weather_id.get(s2_cell_id, Unknown.REGULAR)

    def severity_id(self, s2_cell_id, severity_id=Unknown.REGULAR):
        """ Update and return severity_id for a cell """
        if Unknown.is_not(severity_id):
            self._severity_id[s2_cell_id] = severity_id
        return self._severity_id.get(s2_cell_id, Unknown.REGULAR)

    def day_or_night_id(self, s2_cell_id, day_or_night_id=Unknown.REGULAR):
        """ Update and return day_or_night_id for a cell """
        if Unknown.is_not(day_or_night_id):
            self._day_or_night_id[s2_cell_id] = day_or_night_id
        return self._day_or_night_id.get(s2_cell_id, Unknown.REGULAR)

    def clean_and_save(self):
        """ Cleans the cache and saves the contents if capable. """
        self._clean_hist()
        self._save()

    def _save(self):
        """ Export the data to a more permanent location. """
        pass  # Mem cache isn't backed up.

    def _clean_hist(self):
        """ Clean expired objects to free up memory. """
        for hist in (
                self._mon_hist, self._stop_hist, self._egg_hist,
                self._raid_hist):
            old = []
            now = datetime.utcnow()
            for key, expiration in hist.iteritems():
                if expiration < now:  # Track expired items
                    old.append(key)
            for key in old:  # Remove expired events
                del hist[key]
        self._log.debug("Cleared %s items from cache.", len(old))
