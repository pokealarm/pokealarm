# Standard Library Imports
import copy
import sys
import logging
# 3rd Party Imports
# Local Imports
from Utils import parse_boolean, reject_leftover_parameters, get_team_id, get_move_id, get_pkmn_id, require_and_remove_key, \
    get_dist_as_str


log = logging.getLogger('Filters')

# Maps names to filters.
named_filters = {}

# Maps names to lists of alternative filters.
filter_sets  = {}


# Check if a filter is a Boolean, a Single Filter, or Multiple Filters
def create_multi_filter(location, FilterType, settings, default):
    global named_filters, filter_sets

    bool = parse_boolean(settings)
    if bool is not None:  # Make a new filter off of one of the defaults
        if bool is True:
            return [FilterType({}, default, location)]
        else:
            return None
    elif type(settings) == dict:  # Single literal filter
        return [FilterType(settings, default, location)]
    elif isinstance(settings, list):  # Multiple Filters
        rtn = []
        for filt in settings:
            if type(filt) == dict:
                # We got a literal filter
                rtn.append(FilterType(filt, default, location))
            elif isinstance(filt, basestring) and filt in named_filters:
                # We got a name for a named filter
                rtn.append(FilterType(named_filters[filt].copy(), default, location))
            else:
                log.error("Unknown filter for {}: {}".format(location, str(filt)))
                sys.exit(1)
        return rtn
    elif isinstance(settings, basestring):
        # We got a name that can either reference a filter set or a named filter.
        if settings in filter_sets:
            # We got a name of a filter set - call recursively with the filter set
            return create_multi_filter(location, FilterType, copy.deepcopy(filter_sets[settings]), default)
        elif settings in named_filters:
            # We got a name of a filter - we use it directly
            return [FilterType(named_filters[settings].copy(), default, location)]

    # All other cases are errors
    log.error("{} contains filter that is not in the proper format. Accepted formats are: ".format(location))
    log.error("'True' for default filter, 'False' for disabled,")
    log.error("{ ... filter info ...} for a single filter,")
    log.error("[ {filter1}, {filter2}, {filter3} ] for multiple filters")
    log.error("or the name of either a filter or a filter set.")
    log.error("Please check the PokeAlarm documentation for more information.")
    sys.exit(1)


def load_filters(settings):
    global named_filters, filter_sets

    named_filters = settings.pop("filters", {})
    # Store filter name in filter for nicer logging output
    for filter_name, filter in named_filters.iteritems():
        filter['name'] = filter_name

    filter_sets = {}
    # Expand filter names to filters in filter sets
    for filter_set_name, filter_set in settings.pop('filter_sets', {}).iteritems():
        fset_expanded = []
        for filter in filter_set:
            if isinstance(filter, basestring) and filter in named_filters:
                fset_expanded.append(named_filters[filter])
            elif type(filter) == dict:
                fset_expanded.append(filter)
            else:
                log.error("Unsupported filter set: {} -> {}".format(filter_set_name, str(filter)))
                sys.exit(1)
        filter_sets[filter_set_name] = fset_expanded


def load_pokemon_section(settings):
    log.info("Setting Pokemon filters...")
    pokemon = { "enabled": bool(parse_boolean(settings.pop('enabled', None)) or False) }

    # Determine Pokemon defaults - start with ANY filter
    pkmn_defaults = PokemonFilter.get_defaults()
    user_defaults = settings.pop("default", {})
    if type(user_defaults) == list:
        log.error("Default Pokemon filter cannot be a list '[...]'.")
        log.error("Use a dict '{...}' or filter name instead.")
        log.error("Please see PokeAlarm documentation for proper Filter file formatting.")
        sys.exit(1)
    default_filter = create_multi_filter("user defaults", PokemonFilter, user_defaults, pkmn_defaults)[0]
    log.info("Global Pokemon defaults: {}".format(default_filter.to_string()))
    defaults = default_filter.to_dict()

    # Add the filters to the settings
    filters = {}
    for name in settings:
        pkmn_id = get_pkmn_id(name)
        if pkmn_id is None:
            log.error("Unable to find pokemon named '{}'...".format(name))
            log.error("Please see PokeAlarm documentation for proper Filter file formatting.")
            sys.exit(1)
        if pkmn_id in pokemon:
            log.error("Multiple entries detected for Pokemon #{}. Please remove any extra names.")
            sys.exit(1)
        f = create_multi_filter(name, PokemonFilter, settings[name], defaults)
        if f is not None:
            filters[pkmn_id] = f
    pokemon['filters'] = filters
    # Output filters
    log.debug(filters)
    for pkmn_id in sorted(filters):
        log.debug("The following filters are set for #{}:".format(pkmn_id))
        for i in range(len(filters[pkmn_id])):
            log.debug("F#{}: ".format(i) + filters[pkmn_id][i].to_string())

    return pokemon


def load_pokestop_section(settings):
    log.info("Setting Pokestop filters...")
    stop = {
        "enabled": bool(parse_boolean(require_and_remove_key('enabled', settings, 'Pokestops')) or False),
        "filters": create_multi_filter('Pokestops --> filters', PokestopFilter,
                                       settings.pop('filters', "False"), PokestopFilter.get_defaults())
    }
    reject_leftover_parameters(settings, "Pokestops section of Filters file.")
    for i in range(len(stop['filters'])):
        log.debug("F#{}: ".format(i) + stop['filters'][i].to_string())
    return stop


def load_gym_section(settings):
    log.info("Setting Gym filters...")
    # Set the defaults for "True"
    # Override defaults using a new Filter to verify inputs
    default_filt = GymFilter(settings.pop('default', {}), GymFilter.get_defaults(), 'default')
    default = default_filt.to_dict()
    # Create the settings for gyms
    gym = {
        "enabled": bool(parse_boolean(settings.pop('enabled', None)) or False),
        "ignore_neutral": bool(parse_boolean(settings.pop('ignore_neutral', None)) or False),
        "filters": create_multi_filter('Gym --> filters', GymFilter,
                                       settings.pop('filters', "False"), default)
    }

    reject_leftover_parameters(settings, 'Gym section of Filters file.')  # Check for leftovers
    for i in range(len(gym['filters'])):
        log.debug("F#{}: ".format(i) + gym['filters'][i].to_string())
    return gym


# Base filter class. Every filter may contain at least these criteria.
class Filter(object):

    def __init__(self, settings, default, location):
        """ Abstract class used to define identify and group limits on when notifications are sent. """
        self.name = settings.pop('name', None)
        self.min_dist = float(settings.pop('min_dist', None) or default['min_dist'])
        self.max_dist = float(settings.pop('max_dist', None) or default['max_dist'])

    # Returns the system default filter values.
    @staticmethod
    def get_defaults():
        return {
            "min_dist": 0.0, "max_dist": float('inf')
        }

    # Checks the given distance against this filter
    def check_dist(self, dist):
        return self.min_dist <= dist <= self.max_dist

    # Convert filter to a dict. Helpful in logging situations.
    def to_dict(self):
        return {"min_dist": self.min_dist, "max_dist": self.max_dist}

    # Pretty print this filter to a string.
    def to_string(self):
        defaults = Filter.get_defaults()
        parts = []
        if self.name:
            parts.append("\"{}\":".format(self.name))
        if self.min_dist != defaults["min_dist"] or self.max_dist != defaults["max_dist"]:
            parts.append("Dist: {} to {}".format(get_dist_as_str(self.min_dist), get_dist_as_str(self.max_dist)))
        return " ".join(parts)


#  Used to determine when Pokemon notifications will be triggered.
class PokemonFilter(Filter):

    def __init__(self, settings, default, location):
        super(PokemonFilter, self).__init__(settings, default, location)
        # Do we ignore pokemon with missing info?
        self.ignore_missing = bool(parse_boolean(settings.pop('ignore_missing', default['ignore_missing'])))
        # IVs
        self.min_iv = float(settings.pop('min_iv', None) or default['min_iv'])
        self.max_iv = float(settings.pop('max_iv', None) or default['max_iv'])
        self.min_atk = int(settings.pop('min_atk', None) or default['min_atk'])
        self.max_atk = int(settings.pop('max_atk', None) or default['max_atk'])
        self.min_def = int(settings.pop('min_def', None) or default['min_def'])
        self.max_def = int(settings.pop('max_def', None) or default['max_def'])
        self.min_sta = int(settings.pop('min_sta', None) or default['min_sta'])
        self.max_sta = int(settings.pop('max_sta', None) or default['max_sta'])
        # Size
        self.sizes = PokemonFilter.check_sizes(settings.pop("size", default['size']))
        # Moves - These can't be set in the default filter
        self.req_quick_move = PokemonFilter.create_moves_list(settings.pop("quick_move", default['quick_move']))
        self.req_charge_move = PokemonFilter.create_moves_list(settings.pop("charge_move", default['charge_move']))
        self.req_moveset = PokemonFilter.create_moveset_list(settings.pop("moveset",  default['moveset']))

        reject_leftover_parameters(settings, "pokemon filter under '{}'".format(location))

    # Checks the IV percent against this filter
    def check_iv(self, dist):
        return self.min_iv <= dist <= self.max_iv

    # Checks the attack IV against this filter
    def check_atk(self, atk):
        return self.min_atk <= atk <= self.max_atk

    # Checks the defense IV against this filter
    def check_def(self, def_):
        return self.min_def <= def_ <= self.max_def

    # Checks the stamina IV against this filter
    def check_sta(self, sta):
        return self.min_sta <= sta <= self.max_sta

    # Checks the quick move against this filter
    def check_quick_move(self, move_id):
        if self.req_quick_move is None:
            return True
        return move_id in self.req_quick_move

    # Checks the charge move against this filter
    def check_charge_move(self, move_id):
        if self.req_charge_move is None:
            return True
        return move_id in self.req_charge_move

    # Checks if this combination of moves is in this filter
    def check_moveset(self, move_1_id, move_2_id):
        if self.req_moveset is None:
            return True
        for filt in self.req_moveset:
            if move_1_id in filt and move_2_id in filt:
                return True
        return False

    # Checks the size against this filter
    def check_size(self, size):
        if self.sizes is None:
            return True
        return size in self.sizes

    # Convert this filter to a dict
    def to_dict(self):
        rtn = super(PokemonFilter, self).to_dict()
        rtn.update({
            "min_iv": self.min_iv, "max_iv": self.max_iv,
            "min_atk": self.min_atk, "max_atk": self.max_atk,
            "min_def": self.min_def, "max_def": self.max_def,
            "min_sta": self.min_sta, "max_sta": self.max_sta,
            "quick_move": self.req_quick_move, "charge_move": self.req_charge_move,
            "moveset": self.req_moveset,
            "size": self.sizes,
            "ignore_missing": self.ignore_missing
        })
        return rtn

    # Print this filter
    def to_string(self):
        defaults = PokemonFilter.get_defaults()
        parts = []
        name_or_dist = super(PokemonFilter, self).to_string()
        if name_or_dist:
            parts.append(name_or_dist)
        if self.min_iv != defaults["min_iv"] or self.max_iv != defaults["max_iv"]:
            parts.append("IV: {}% to {}%".format(self.min_iv, self.max_iv))
        if self.min_atk != defaults["min_atk"] or self.max_atk != defaults["max_atk"]:
            parts.append("Atk: {} to {}".format(self.min_atk, self.max_atk))
        if self.min_def != defaults["min_def"] or self.max_def != defaults["max_def"]:
            parts.append("Def: {} to {}".format(self.min_def, self.max_def))
        if self.min_sta != defaults["min_sta"] or self.max_sta != defaults["max_sta"]:
            parts.append("Atk: {} to {}".format(self.min_sta, self.max_sta))
        if self.req_quick_move is not None:
            parts.append("Quick Moves: {}".format(self.req_quick_move))
        if self.req_charge_move is not None:
            parts.append("Charge Moves: {}".format(self.req_charge_move))
        if self.req_moveset is not None:
            parts.append("Move Sets: {}".format(self.req_moveset))
        if self.sizes is not None:
            parts.append("Sizes: {}".format(self.sizes))
        if self.ignore_missing != defaults["ignore_missing"]:
            parts.append("Ignore Missing: {}".format(self.ignore_missing))
        if not parts:
            parts.append("any")
        return ", ".join(parts)

    @staticmethod
    def get_defaults():
        rtn = super(PokemonFilter, PokemonFilter).get_defaults()
        rtn.update({
            "ignore_missing": False,
            "min_iv": 0.0, "max_iv": 100.0,
            "min_atk": 0, "max_atk": 15,
            "min_def": 0, "max_def": 15,
            "min_sta": 0, "max_sta": 15,
            "quick_move": None, "charge_move": None, "moveset": None,
            "size": None
        })
        return rtn

    @staticmethod
    def create_moves_list(moves):
        if moves is None:  # no moves
            return None
        if type(moves) != list:
            log.error("Moves list must be in a comma seperated array. Ex: [\"Move\",\"Move\"]"
                      + "Please see PokeAlarm documentation for more examples.")
            sys.exit(1)
        list_ = set()
        for move_name in moves:
            move_id = get_move_id(move_name)
            if move_id is not None:
                list_.add(move_id)
            else:
                log.error("{} is not a valid move name.".format(move_name)
                          + "Please see documentation for accepted move names and correct your Filters file.")
                sys.exit(1)
        return list_

    @staticmethod
    def create_moveset_list(moves):
        if moves is None:  # no moveset
            return None
        list_ = []
        for moveset in moves:
            list_.append(PokemonFilter.create_moves_list(moveset.split('/')))
        return list_

    @staticmethod
    def check_sizes(sizes):
        if sizes is None:  # no sizes
            return None
        list_ = set()
        valid_sizes = ['tiny', 'small', 'normal', 'large', 'big']
        for raw_size in sizes:
            size = raw_size
            if size in valid_sizes:
                list_.add(size)
            else:
                log.error("{} is not a valid size name.".format(size))
                log.error("Please use one of the following: {}".format(valid_sizes))
                sys.exit(1)
        return list_


# Pokestop Filter is used to determine when Pokestop notifications will be triggered.
class PokestopFilter(Filter):

    def __init__(self, settings, default, location):
        super(PokestopFilter, self).__init__(settings, default, location)

        reject_leftover_parameters(settings, "Pokestop filter in {}".format(location))


# GymFilter is used to determine when Gym notifications will be triggered.
class GymFilter(Filter):

    def __init__(self, settings, default, location):
        super(GymFilter, self).__init__(settings, default, location)

        # Check for 'To Team' list
        self.to_team = GymFilter.create_team_list(settings.pop('to_team'))  \
            if 'to_team' in settings else default['to_team'].copy()
        # Check for 'From Team' list
        self.from_team = GymFilter.create_team_list(settings.pop('from_team')) \
            if 'from_team' in settings else default['to_team'].copy()

        reject_leftover_parameters(settings, "Gym filter in {}".format(location))

    def check_from_team(self, team_id):
        return team_id in self.from_team

    def check_to_team(self, team_id):
        return team_id in self.to_team

    def to_dict(self):
        rtn = super(GymFilter, self).to_dict()
        rtn.update({
            "to_team": self.to_team, "from_team": self.from_team
        })
        return rtn

    def to_string(self):
        parts = []
        name_or_dist = super(GymFilter, self).to_string()
        if name_or_dist:
            parts.append(name_or_dist)
        parts.append("Team(s) {} changes to Team(s) {}".format(self.from_team, self.to_team))
        return ", ".join(parts)

    @staticmethod
    def get_defaults():
        rtn = super(GymFilter, GymFilter).get_defaults()
        rtn.update({
            "to_team": {0, 1, 2, 3}, "from_team": {0, 1, 2, 3}
        })
        return rtn

    @staticmethod
    def create_team_list(settings):  # Create a set of Team ID #'s
        if type(settings) != list:
            log.error("Gym names must be specified in an array. EX: "
                      + "[\"Valor\", \"Instinct\"]" )
            sys.exit(1)
        s = set()
        for team in settings:
            team_id = get_team_id(team)
            if team_id is not None:
                s.add(team_id)
            else:  # If no team ID
                log.error("{} is not a valid team name.".format(team)
                          + "Please see documentation for accepted team names and correct your Filters file.")
                sys.exit(1)
        return s


class Geofence(object):

    # Expects points to be
    def __init__(self, name, points):
        self.name = name
        self.__points = points

        self.__min_x = points[0][0]
        self.__max_x = points[0][0]
        self.__min_y = points[0][1]
        self.__max_y = points[0][1]

        for p in points:
            self.__min_x = min(p[0], self.__min_x)
            self.__max_x = max(p[0], self.__max_x)
            self.__min_y = min(p[1], self.__min_y)
            self.__max_y = max(p[1], self.__max_y)

    def contains(self, x, y):
        # Quick check the boundary box of the entire polygon
        if self.__max_x < x or x < self.__min_x or self.__max_y < y or y < self.__min_y:
            return False

        inside = False
        p1x, p1y = self.__points[0]
        n = len(self.__points)
        for i in range(1, n+1):
            p2x, p2y = self.__points[i % n]
            if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def get_name(self):
        return self.__name