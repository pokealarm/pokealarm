# Standard Library Imports
from glob import glob
import json

# 3rd Party Imports
# Local Imports
from PokeAlarm.Utils import get_path


# Returns type of quest reward (e.g. monster, dust, etc.)
def get_reward_type(reward_type):
    try:
        name = str(reward_type).lower()
        if not hasattr(get_reward_type, "ids"):
            get_reward_type.ids = {}
            files = glob(get_path("locales/*.json"))
            for file_ in files:
                with open(file_, "r") as f:
                    j = json.loads(f.read())
                    j = j["quest_reward_types"]
                    for id_ in j:
                        nm = j[id_].lower()
                        get_reward_type.ids[nm] = int(id_)
        if name in get_reward_type.ids:
            return get_reward_type.ids[name]
        else:
            return int(name)  # try as an integer
    except ValueError:
        raise ValueError(
            f"Unable to interpret '{reward_type}' as a valid quest reward type or id."
        )


def reward_string(quest, locale):
    if quest.reward_type_id == 7:  # reward type is monster
        return locale.get_quest_monster_reward(
            {
                "id": quest.monster_id,
                "form": quest.monster_form_id,
                "costume": quest.monster_costume_id,
            }
        )
    elif quest.reward_type_id == 2:  # reward type is item
        return locale.get_quest_item_reward(
            {"id": quest.item_id, "type": quest.item_type, "amount": quest.item_amount}
        )
    elif quest.reward_type_id == 0:  # reward type is unset
        return locale.get_quest_type_name(0)

    # Assume generic reward type
    return locale.get_quest_generic_reward(quest.reward_type_id, quest.reward_amount)


def get_item_id(item_name):
    try:
        name = str(item_name).lower()
        if not hasattr(get_item_id, "ids"):
            get_item_id.ids = {}
            files = glob(get_path("locales/*.json"))
            for file_ in files:
                with open(file_, "r") as f:
                    j = json.loads(f.read())
                    j = j["items"]
                    for id_ in j:
                        nm = j[id_].lower()
                        get_item_id.ids[nm] = int(id_)
        if name in get_item_id.ids:
            return get_item_id.ids[name]
        else:
            return int(name)  # try as an integer
    except Exception:
        raise ValueError(
            f"Unable to interpret '{item_name}' as a valid item name or id."
        )


def get_quest_image(quest):
    image = ""
    if quest.reward_type_id == 7:  # reward type is monster
        return f"{image}monsters/{quest.monster_id:03}_{quest.monster_form_id:03d}"
    elif quest.reward_type_id == 2:  # reward type is item
        return f"{image}items/{quest.item_id:04d}"

    # Assume generic reward type
    return f"{image}quests/{quest.reward_type_id:03d}"
