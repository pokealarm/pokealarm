import os
import logging
import datetime

from .. import config

log = logging.getLogger(__name__)

def get_args():
	#parser = configargparse.ArgParser(default_config_files=[configpath])
	parser.add_argument('-H', '--host', help='Set web server listening host', default='127.0.0.1')
	parser.add_argument('-P', '--port', type=int, help='Set web server listening port', default=4000)
	parser.add_argument('-L', '--locale', help='Locale for Pokemon names: default en, check locale folder for more options', default='en')
	parser.set_defaults(DEBUG=False)

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
    if not hasattr(get_pokemon_name, 'names'):
        file_path = os.path.join(
            config['ROOT_PATH'],
            config['LOCALES_DIR'],
            'pokemon.{}.json'.format(config['LOCALE']))

        with open(file_path, 'r') as f:
            get_pokemon_name.names = json.loads(f.read())

    return get_pokemon_name.names[str(pokemon_id)]