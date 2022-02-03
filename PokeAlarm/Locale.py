# Standard Library Imports
import os
import json
import logging
# 3rd Party Imports
# Local Imports
from .Utils import get_path

log = logging.getLogger('Locale')


# Locale object is used to get different translations in other languages
class Locale(object):

    name = 'en'

    # Load in the locale information from the specified json file
    def __init__(self, language):
        # Set language name
        self.name = language
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
        for id_, val in default["pokemon"].items():
            self.__pokemon_names[int(id_)] = pokemon.get(id_, val)

        # Pokemon ID -> Explicitly English Name
        self.__english_pokemon_names = {}
        pokemon = default.get("pokemon", {})
        for id_, val in default["pokemon"].items():
            self.__english_pokemon_names[int(id_)] = pokemon.get(id_, val)

        # Move ID -> Name
        self.__move_names = {}
        moves = info.get("moves", {})
        for id_, val in default["moves"].items():
            self.__move_names[int(id_)] = moves.get(id_, val)

        # Team ID -> Name
        self.__team_names = {}
        teams = info.get("teams", {})
        for id_, val in default["teams"].items():
            self.__team_names[int(id_)] = teams.get(id_, val)

        # Team ID -> Color
        self.__team_colors = {}
        team_colors = info.get("team_colors", {})
        for id_, val in default["team_colors"].items():
            self.__team_colors[int(id_)] = team_colors.get(id_, val)

        # Team ID -> Team Leaders
        self.__leader_names = {}
        leaders = info.get("leaders", {})
        for id_, val in default["leaders"].items():
            self.__leader_names[int(id_)] = leaders.get(id_, val)

        # Weather ID -> Name
        self.__weather_names = {}
        weather = info.get("weather", {})
        for id_, val in default["weather"].items():
            self.__weather_names[int(id_)] = weather.get(id_, val)

        # Size ID -> Size Name
        self.__size_names = {}
        sizes = info.get("sizes", {})
        for id_, val in default["sizes"].items():
            self.__size_names[int(id_)] = sizes.get(id_, val)

        # Type ID -> Type Name
        self.__type_names = {}
        types = info.get("types", {})
        for id_, val in default["types"].items():
            self.__type_names[int(id_)] = types.get(id_, val)

        # Pokemon ID -> { Costume ID -> Costume Name}
        self.__costume_names = {}
        all_costumes = info.get("costumes", {})
        for pkmn_id, costumes in default["costumes"].items():
            self.__costume_names[int(pkmn_id)] = {}
            pkmn_costumes = all_costumes.get(pkmn_id, {})
            for costume_id, costume_name in costumes.items():
                self.__costume_names[int(pkmn_id)][int(
                    costume_id)] = pkmn_costumes.get(costume_id, costume_name)

        # Pokemon ID -> { Form ID -> Form Name}
        self.__form_names = {}
        all_forms = info.get("forms", {})
        for pkmn_id, forms in default["forms"].items():
            self.__form_names[int(pkmn_id)] = {}
            pkmn_forms = all_forms.get(pkmn_id, {})
            for form_id, form_name in forms.items():
                self.__form_names[int(pkmn_id)][int(form_id)] = pkmn_forms.get(
                    form_id, form_name)

        # Pokemon ID -> { Form ID -> Explicitly English Form Name }
        self.__english_form_names = {}
        english_forms = default.get('forms', {})
        for pkmn_id, forms in default['forms'].items():
            self.__english_form_names[int(pkmn_id)] = {}
            pkmn_forms = english_forms.get(pkmn_id, {})
            for form_id, form_name in forms.items():
                self.__english_form_names[int(pkmn_id)][int(form_id)] = \
                    pkmn_forms.get(form_id, form_name)

        # Rarity ID -> Rarity Name
        self.__rarity_names = {}
        rarity_names = info.get("rarity", {})
        for _id, rarity in default["rarity"].items():
            self.__rarity_names[int(_id)] = rarity_names.get(_id, rarity)

        # Severity ID -> Severity Name
        self.__severity_names = {}
        severities = info.get("severity", {})
        for id_, val in default["severity"].items():
            self.__severity_names[int(id_)] = severities.get(id_, val)

        # Day or Night ID -> Day or Night Name
        self.__day_or_night_names = {}
        day_or_night = info.get('day_or_night', {})
        for id_, val in default['day_or_night'].items():
            self.__day_or_night_names[int(id_)] = day_or_night.get(id_, val)

        # Quest Type ID -> Quest Type Name
        self.__quest_type_names = {}
        quest_reward_types = info.get('quest_reward_types', {})
        for id_, val in default['quest_reward_types'].items():
            self.__quest_type_names[int(id_)] = \
                quest_reward_types.get(id_, val)

        # Item ID -> Item Name
        self.__item_names = {}
        items = info.get('items', {})
        for id_, val in default['items'].items():
            self.__item_names[int(id_)] = items.get(id_, val)

        # Lure Type ID -> Lure Type Name
        self.__lure_type_names = {}
        lure_types = info.get('lure_types', {})
        for id_, val in default['lure_types'].items():
            self.__lure_type_names[int(id_)] = lure_types.get(id_, val)

        # Grunt ID -> Grunt Type Name
        self.__grunt_type_names = {}
        grunt_types = info.get('grunt_types', {})
        for id_, val in default['grunt_types'].items():
            self.__grunt_type_names[int(id_)] = grunt_types.get(id_, val)

        # Grunt ID -> Grunt Gender
        self.__grunt_genders = {}
        grunt_genders = info.get('grunt_genders', {})
        for id_, val in default['grunt_genders'].items():
            self.__grunt_genders[int(id_)] = grunt_genders.get(id_, val)

        # Evolution ID -> Evolution Name
        self.__evolutions_names = {}
        evolutions = info.get('evolutions', {})
        for id_, val in default['evolutions'].items():
            self.__evolutions_names[int(id_)] = evolutions.get(id_, val)

        log.debug("Loaded '{}' locale successfully!".format(language))

        self.__misc = info.get('misc', {})

    # Returns the name of the Pokemon associated with the given ID
    def get_pokemon_name(self, pokemon_id):
        return self.__pokemon_names.get(pokemon_id, 'unknown')

    # Returns the English name of the Pokemon associated with the given ID
    def get_english_pokemon_name(self, pokemon_id):
        return self.__english_pokemon_names.get(pokemon_id, 'unknown')

    def get_english_form_name(self, pokemon_id, form_id):
        return self.__english_form_names.get(pokemon_id, {}).get(
            form_id, 'unknown')

    # Returns the name of the move associated with the move ID
    def get_move_name(self, move_id):
        return self.__move_names.get(move_id, 'unknown')

    # Returns the name of the team associated with the Team ID
    def get_team_name(self, team_id):
        return self.__team_names.get(team_id, 'unknown')

    # Returns the name of the team leader associated with the Team ID
    def get_leader_name(self, team_id):
        return self.__leader_names.get(team_id, 'unknown')

    # Returns the name of the color associated with the Team ID
    def get_team_color(self, team_id):
        return self.__team_colors.get(team_id, 'unknown')

    # Returns the name of the weather associated with the given ID
    def get_weather_name(self, weather_id):
        return self.__weather_names.get(weather_id, 'unknown')

    # Returns the size of the Pokemon based on the Calculated Size Value
    def get_size_name(self, size_id):
        return self.__size_names.get(size_id, 'unknown')

    # Returns the name of the type associated with the Type ID
    def get_type_name(self, type_id):
        return self.__type_names.get(type_id, 'unknown')

    # Returns the name of the form of for the given Pokemon ID and Form ID
    def get_form_name(self, pokemon_id, form_id):
        return self.__form_names.get(pokemon_id, {}).get(form_id, 'unknown')

    # Returns the name of the evolution for the given Evolution ID
    def get_evolution_name(self, evolution_id):
        return self.__evolutions_names.get(evolution_id, 'unknown')

    # Returns the name of the costume for the given Pokemon ID and Costume ID
    def get_costume_name(self, pokemon_id, costume_id):
        return self.__costume_names.get(
            pokemon_id, {}).get(costume_id, 'unknown')

    # Returns the rarity corresponding to the id
    def get_rarity_name(self, rarity_id):
        return self.__rarity_names.get(rarity_id, 'unknown')

    def get_boosted_text(self):
        return self.__misc.get('boosted', '')

    def get_severity_name(self, severity_id):
        return self.__severity_names.get(severity_id, 'unknown')

    def get_day_or_night(self, day_or_night_id):
        return self.__day_or_night_names.get(day_or_night_id, 'unknown')

    def get_quest_type_name(self, quest_type_id):
        return self.__quest_type_names.get(quest_type_id, 'unknown')

    def get_lure_type_name(self, lure_type_id):
        return self.__lure_type_names.get(lure_type_id, 'unknown')

    def get_grunt_type_name(self, grunt_type_id):
        return self.__grunt_type_names.get(grunt_type_id, 'unknown')

    def get_grunt_gender_name(self, grunt_type_id):
        return self.__grunt_genders.get(grunt_type_id, 'unknown')

    def adjective_placement(self):
        """ true is before, false is after """
        return self.name in ['en', 'de']

    def get_quest_monster_reward(self, monster):
        reward_template = '{form_with_space}{monster}'
        if not self.adjective_placement():
            reward_template = '{monster} {form}'
        return reward_template.format(
            # costume_with_space=
            # (self.get_costume_name(monster.id, monster.costume) + ' '
            #  if monster.costume != 0 else ''),
            # costume=self.get_costume_name(monster.id, monster.costume),
            form=self.get_form_name(monster['id'], monster['form']),
            form_with_space=self.get_form_name(monster['id'], monster['form'])
            + ' '
            if monster['form'] != 0 and self.get_form_name(
                monster['id'], monster['form']) not in ['Normal', 'Normale']
            else '',
            monster=self.get_pokemon_name(monster['id']))

    def get_quest_item_reward(self, item):
        item_name = self.get_item_name(item['id'])
        reward_template = '{amount} {item}'
        if not self.adjective_placement():
            reward_template = '{item} {amount}'
        return reward_template.format(
            amount=item['amount'],
            type=item['type'],
            item=item_name)

    def get_quest_generic_reward(self, reward_type_id, reward_amount):
        reward_name = self.get_quest_type_name(reward_type_id)
        if self.adjective_placement():
            return '{reward_amount} {reward_name}'.format(
                reward_amount=reward_amount, reward_name=reward_name)
        return '{reward_name} {reward_amount}'.format(
            reward_name=reward_name, reward_amount=reward_amount)

    def get_item_name(self, item_id):
        return self.__item_names.get(item_id, 'unknown')

    def get_pvpoke_domain(self):
        if self.name == 'de':
            return 'de.pvpoke-re.com'
        elif self.name == 'fr':
            return 'fr.pvpoke-re.com'
        elif self.name == 'es':
            return 'es.pvpoke-re.com'
        elif self.name == 'pt':
            return 'pt.pvpoke-re.com'
        else:
            return 'pvpoke.com'
