import os
import json
import logging
from datetime import datetime
import configargparse

from .. import config

log = logging.getLogger(__name__)

def set_config(root_path):
	parser = configargparse.ArgParser()
	parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
	parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=4000)
	parser.add_argument('-L', '--locale', help='Locale for Pokemon names: default en, check locale folder for more options', default='en')
	parser.add_argument('-d', '--debug', help='Debug Mode', action='store_true')
	parser.set_defaults(DEBUG=False)
	
	args = parser.parse_args()
	
	config['ROOT_PATH'] = root_path
	config['HOST'] = args.host
	config['PORT'] = args.port
	config['LOCALE'] = args.locale
	config['DEBUG'] = args.debug
	
	return config

def pkmn_alert_text(name):
	return "A wild " + pokemon['name'].title() + " has appeared!"
	
def gmaps_link(lat, lng):
		latLon = '{},{}'.format(repr(lat), repr(lng))
		return 'http://maps.google.com/maps?q={}'.format(latLon)
		
def pkmn_time_text(time):
		s = (time - datetime.utcnow()).total_seconds()
		(m, s) = divmod(s, 60)
		(h, m) = divmod(m, 60)
		d = timedelta(hours = h, minutes = m, seconds = s)
		disappear_time = datetime.now() + d
		return "Available until %s (%dm %ds)." % (disappear_time.strftime("%H:%M:%S"),m,s)
	

def pkmn_name(pokemon_id):
    if not hasattr(pkmn_name, 'names'):
        file_path = os.path.join(
            config['ROOT_PATH'],
            config['LOCALES_DIR'],
            'pokemon.{}.json'.format(config['LOCALE']))

        with open(file_path, 'r') as f:
            pkmn_name.names = json.loads(f.read())

    return pkmn_name.names[str(pokemon_id)]