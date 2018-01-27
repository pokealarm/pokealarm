import json
import sys
import os
from collections import OrderedDict


def exchange(key):
    return {
        "pokemon": "monsters",
        "pokestop": "stops",
        "gym": "gyms",
        "egg": "eggs",
        "raid": "raids",
        "stickers": "sticker",
        "location": "map",
        "disable_map_notification": "map_notify",
    }.get(key, key)


def exchange_set(settings):
    if type(settings) != OrderedDict:
        return settings
    new_settings = OrderedDict()
    for key in settings:
        new_settings[exchange(key)] = exchange_set(settings[key])
    return new_settings


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: convert_alarms_file.py /path/to/alarms.json"
        print ("This utility will rename your old file and write "
               "a converted one in it's place")
        exit(0)

    contents = None
    try:
        print "Loading alarms file from {}.".format(sys.argv[1])
        with open(sys.argv[1], 'r') as f:
            contents = json.load(f, object_pairs_hook=OrderedDict)
    except ValueError as e:
        print ("Encounter a ValueError while loading the file. Make sure "
               "your file is in the correct JSON format then try again.")
    except IOError as e:
        print ("Unable to find file. Please check that the file exists "
               "and the program has the proper privileges then try again.")
    except Exception as e:
        print ("An unexpected error as occurred: {} - {}"
               "".format(type(e).__name__, e))
    if not contents:
        exit()

    output = OrderedDict()
    print "Processing file..."
    for i in range(len(contents)):
        output["alarm_{}".format(i)] = exchange_set(contents[i])

    try:
        old_path = sys.argv[1] + ".old"
        print "Renaming old file to {}.".format(old_path)
        os.rename(sys.argv[1], old_path)
        print "Writing to new file at {}.".format(sys.argv[1])
        with open(sys.argv[1], 'w') as f:
            json.dump(output, f, indent=4)
    except IOError as e:
        print ("Unable to write to file. Please check that the "
               "program has the proper privileges then try again.")
        exit(1)
    except Exception as e:
        print ("An unexpected error as occurred: {} - {}"
               "".format(type(e).__name__, e))
        exit(1)

    print ("Conversion finished! If you are a telegram user, verify your"
           "settings as some of them have inversed.")
