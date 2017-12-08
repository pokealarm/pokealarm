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

        # Team ID -> Team Leaders
        self.__leader_names = {}
        leaders = info.get("leaders", {})
        for id_, val in default["leaders"].iteritems():
            self.__leader_names[int(id_)] = leaders.get(id_, val)

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

    # Returns the name of the Pokemon associated with the given ID
    def get_pokemon_name(self, pokemon_id):
        return self.__pokemon_names.get(pokemon_id, 'unknown')

    # Returns the name of the move associated with the move ID
    def get_move_name(self, move_id):
        return self.__move_names.get(move_id, 'unknown')

    # Returns the name of the team associated with the Team ID
    def get_team_name(self, team_id):
        return self.__team_names.get(team_id, 'unknown')

    # Returns the name of the team ledaer associated with the Team ID
    def get_leader_name(self, team_id):
        return self.__leader_names.get(team_id, 'unknown')

    # Returns the name of the form of for the given Pokemon ID and Form ID
    def get_form_name(self, pokemon_id, form_id):
        return self.__form_names.get(pokemon_id, {}).get(form_id, 'unknown')
