# Standard Library Imports
from datetime import datetime
import logging
import multiprocessing
# 3rd Party Imports
# Local Imports
from Utils import get_gmaps_link

log = logging.getLogger(__name__)


# PokemonGo-Map Standards
class PokemonGoMap:

    def __init__(self):
        raise NotImplementedError("This is a static class not meant to be initiated")

    @staticmethod
    def make_object(data):
        kind = data.get('type')
        if kind == 'pokemon':
            return PokemonGoMap.pokemon(data.get('message'))
        elif data['type'] == 'pokestop':
            return PokemonGoMap.pokestop(data.get('message'))
        elif data['type'] == 'gym' or data['type'] == 'gym_details':
            return PokemonGoMap.gym(data.get('message'))
        log.error("Invalid type specified ({}). Are you using the correct map type?".format(type))
        return None

    @staticmethod
    def pokemon(data):
        pkmn = {
            'type': "pokemon",
            'id': data['encounter_id'],
            'pkmn_id': int(data['pokemon_id']),
            'disappear_time': datetime.utcfromtimestamp(data['disappear_time']),
            'lat': float(data['latitude']),
            'lng': float(data['longitude']),
        }
        pkmn['gmaps'] = get_gmaps_link(pkmn['lat'], pkmn['lng'])

        if all(move in data for move in ['move_1', 'move_2']):
            pkmn['move_1_id'] = int(data['move_1'])
            pkmn['move_2_id'] = int(data['move_2'])
        else:
            pkmn['move_1_id'], pkmn['move_2_id'] = 'unkown'

        if all(iv in data for iv in ['individual_attack', 'individual_defense', 'individual_stamina']):
            atk = int(data.get('individual_attack'))
            def_ = int(data.get('individual_defense'))
            sta = int(data.get('individual_stamina'))
            pkmn['atk'], pkmn['def'], pkmn['sta'] = atk, def_, sta
            pkmn['iv'] = float(((atk + def_ + sta)*100)/float(45))
        else:
            pkmn['iv'], pkmn['atk'], pkmn['def'], pkmn['sta'] = 'unkn'
        return pkmn

    @staticmethod
    def pokestop(data):
        stop = {
            'type': "pokestop",
            'id': data['pokestop_id'],
            'expire_time':  datetime.utcfromtimestamp(data['lure_expiration']),
            'lat': float(data['latitude']),
            'lng': float(data['longitude'])
        }
        stop['gmaps'] = get_gmaps_link(stop['lat'], stop['lng'])
        return stop

    @staticmethod
    def gym(data):
        gym = {
            'type': "gym",
            'id': data['gym_id'],
            "team_id": int(data['team_id']),
            "points": int(data['gym_points']),
            "guard_pkmn_id": int(data['guard_pokemon_id']),
            'lat': float(data['latitude']),
            'lng': float(data['longitude'])
        }
        gym['gmaps'] = get_gmaps_link(gym['lat'], gym['lng'])
        return gym


# Class to allow optimization of waiting requests (not process sage)
class QueueSet(object):
    def __init__(self):
        self.__queue = multiprocessing.Queue()
        self.__lock = multiprocessing.Lock()
        self.__data_set = {}  # TODO: This set will probably not be process safe... so that is a thing

    # Add or update an object to the QueueSet
    def add(self, id, obj):
        self.__lock.acquire()
        try:
            if id not in self.__data_set:
                self.__queue.put(id)
            self.__data_set[id] = obj  # Update info incase it had changed
        except Exception as e:
            log.error("QueueSet error encountered in add: \n {}".format(e))
        finally:
            self.__lock.release()

    # Remove the next item in line
    def remove_next(self):
        self.__lock.acquire()
        data = None
        try:
            id = self.__queue.get(block=True)  # get the next id
            data = self.__data_set[id]  # extract the relevant data
            del self.__data_set[id]  # remove the id from the set
        except Exception as e:
            log.error("QueueSet error encountered in remove: \n {}".format(e))
        finally:
            self.__lock.release()
        return data
