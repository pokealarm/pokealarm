# Standard Library Imports
import os
import json
import logging
# 3rd Party Imports
# Local Imports
from Utils import get_path

log = logging.getLogger('Locale')


# Locale object is used to get different translations in other languages
class Locale(object):

    # Load in the locale information from the specified json file
    def __init__(self, language):
        # Load in English as the default
        with open(os.path.join(get_path('locales'), 'en.json')) as f:
            default = json.loads(f.read())
        # Now load in the actual language we want
        # (unnecessary for English but we don't want to discriminate)
        with open(os.path.join(
                get_path('locales'), '{}.json'.format(language))) as f:
            info = json.loads(f.read())

        # Pokemon ID -> Name
        self.__pokemon_names = {}
        pokemon = info.get("pokemon", {})
        for id_, val in default["pokemon"].iteritems():
            self.__pokemon_names[int(id_)] = pokemon.get(id_, val)

        # Move ID -> Name
        self.__move_names = {}
        moves = info.get("moves", {})
        for id_, val in default["moves"].iteritems():
            self.__move_names[int(id_)] = moves.get(id_, val)

        # Team ID -> Name
        self.__team_names = {}
        teams = info.get("teams", {})
        for id_, val in default["teams"].iteritems():
            self.__team_names[int(id_)] = teams.get(id_, val)

        # Item ID -> Name
        self.__item_names = {}
        items = info.get("items", {})
        for id_, val in default["items"].iteritems():
            self.__item_names[int(id_)] = items.get(id_, val)

        # Team ID -> Team Leaders
        self.__leader_names = {}
        leaders = info.get("leaders", {})
        for id_, val in default["leaders"].iteritems():
            self.__leader_names[int(id_)] = leaders.get(id_, val)

        # Weather ID -> Name
        self.__weather_names = {}
        weather = info.get("weather", {})
        for id_, val in default["weather"].iteritems():
            self.__weather_names[int(id_)] = weather.get(id_, val)

        # Size ID -> Size Name
        self.__size_names = {}
        sizes = info.get("sizes", {})
        for id_, val in default["sizes"].iteritems():
            self.__size_names[int(id_)] = sizes.get(id_, val)

        # Type ID -> Type Name
        self.__type_names = {}
        types = info.get("types", {})
        for id_, val in default["types"].iteritems():
            self.__type_names[int(id_)] = types.get(id_, val)

        # Throw Type ID -> Throw Type Name
        self.__throw_type_names = {}
        types = info.get("throw_types", {})
        for id_, val in default["throw_types"].iteritems():
            self.__throw_type_names[int(id_)] = types.get(id_, val)

        # Quest Type ID -> Quest Type Name
        self.__quest_type_names = {}
        types = info.get("quest_types", {})
        for id_, val in default["quest_types"].iteritems():
            self.__quest_type_names[int(id_)] = types.get(id_, val)

        # Pokemon ID -> { Form ID -> Form Name)
        self.__form_names = {}
        all_forms = info.get("forms", {})
        for pkmn_id, forms in default["forms"].iteritems():
            self.__form_names[int(pkmn_id)] = {}
            pkmn_forms = all_forms.get(pkmn_id, {})
            for form_id, form_name in forms.iteritems():
                self.__form_names[int(pkmn_id)][int(form_id)] = pkmn_forms.get(
                    form_id, form_name)
        log.debug("Loaded '{}' locale successfully!".format(language))

        self.__misc = info.get('misc', {})

    # Returns the name of the Pokemon associated with the given ID
    def get_pokemon_name(self, pokemon_id):
        return self.__pokemon_names.get(pokemon_id, 'unknown')

    # Returns the name of the move associated with the move ID
    def get_move_name(self, move_id):
        return self.__move_names.get(move_id, 'unknown')

    # Returns the name of the team associated with the Team ID
    def get_team_name(self, team_id):
        return self.__team_names.get(team_id, 'unknown')

    # Returns the name of the team associated with the Team ID
    def get_item_name(self, item_id):
        return self.__item_names.get(item_id, 'unknown')

    # Returns the name of the team ledaer associated with the Team ID
    def get_leader_name(self, team_id):
        return self.__leader_names.get(team_id, 'unknown')

    # Returns the name of the weather associated with the given ID
    def get_weather_name(self, weather_id):
        return self.__weather_names.get(weather_id, 'unknown')

    # Returns the size of the Pokemon based on the Calculated Size Value
    def get_size_name(self, size_id):
        return self.__size_names.get(size_id, 'unknown')

    # Returns the name of the type associated with the Type ID
    def get_type_name(self, type_id):
        return self.__type_names.get(type_id, 'unknown')

    # Returns the name of the throw type associated with the throw type ID
    def get_throw_type_name(self, throw_type_id):
        return self.__throw_type_names.get(throw_type_id, 'unknown')

    # Returns the name of the quest type associated with the quest type ID
    def get_quest_type_name(self, quest_type_id):
        return self.__quest_type_names.get(quest_type_id, 'unknown')

    # Returns the name of the form of for the given Pokemon ID and Form ID
    def get_form_name(self, pokemon_id, form_id):
        return self.__form_names.get(pokemon_id, {}).get(form_id, 'unknown')

    def get_boosted_text(self):
        return self.__misc.get('boosted', '')

    def get_indefinite_article(self, isVowel):
        if isVowel:
            return self.__misc.get('an', '')
        else:
            return self.__misc.get('a', '')
