#!/usr/bin/python
# -*- coding: utf-8 -*-

# Monkey Patch to allow Gevent's Concurrency
from gevent import monkey
monkey.patch_all()

# Setup Logging
import logging
logging.basicConfig(
    format='%(asctime)s [%(processName)15.15s][%(name)10.10s]'
           + '[%(levelname)8.8s] %(message)s', level=logging.INFO)

# Standard Library Imports

import json
import os
import sys
# 3rd Party Imports
import configargparse
from gevent import wsgi, spawn, signal, pool, queue
from flask import Flask, request, abort
import pytz
# Local Imports
import PokeAlarm.Events as Events
from PokeAlarm import config
from PokeAlarm.Cache import cache_options
from PokeAlarm.Manager import Manager
from PokeAlarm.Utils import get_path, parse_unicode

# Reinforce UTF-8 as default
reload(sys)
sys.setdefaultencoding('UTF8')

# Set up logging

log = logging.getLogger('Server')

# Global Variables
app = Flask(__name__)
data_queue = queue.Queue()
managers = {}
server = None


@app.route('/', methods=['GET'])
def index():
    return "PokeAlarm Running!"


@app.route('/', methods=['POST'])
def accept_webhook():
    try:
        log.debug("POST request received from {}.".format(request.remote_addr))
        data = json.loads(request.data)
        if type(data) == dict:  # older webhook style
            data_queue.put(data)
        else:   # For RM's frame
            for frame in data:
                data_queue.put(frame)
    except Exception as e:
        log.error("Encountered error while receiving webhook "
                  + "({}: {})".format(type(e).__name__, e))
        abort(400)
    return "OK"  # request ok


# Thread used to distribute the data into various processes
def manage_webhook_data(queue):
    while True:
        qsize = queue.qsize()
        if qsize > 5000:
            log.warning("Queue length is at %s... this may be causing "
                        + "a significant delay in notifications.", qsize)
        data = queue.get(block=True)
        obj = Events.event_factory(data)
        if obj is not None:
            for name, mgr in managers.iteritems():
                mgr.update(obj)
                log.debug("Distributing event {} to manager {}.".format(
                    obj.id, name))
            log.debug("Finished distributing event: {}".format(obj.id))


# Configure and run PokeAlarm
def start_server():
    log.setLevel(logging.INFO)
    logging.getLogger('PokeAlarm').setLevel(logging.INFO)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('pywsgi').setLevel(logging.WARNING)
    logging.getLogger('connectionpool').setLevel(logging.WARNING)
    logging.getLogger('gipc').setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    parse_settings(os.path.abspath(os.path.dirname(__file__)))

    # Start Webhook Manager in a Thread
    spawn(manage_webhook_data, data_queue)

    # Start up Server
    log.info("PokeAlarm is listening for webhooks on: http://{}:{}".format(
        config['HOST'], config['PORT']))
    threads = pool.Pool(config['CONCURRENCY'])
    global server
    server = wsgi.WSGIServer(
        (config['HOST'], config['PORT']), app, log=logging.getLogger('pywsgi'),
        spawn=threads)
    server.serve_forever()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CONFIG UTILITIES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def parse_settings(root_path):
    config['ROOT_PATH'] = root_path
    # Set the default config files up
    config_files = [get_path('config/config.ini')]
    if '-cf' in sys.argv or '--config' in sys.argv:
        config_files = []
    parser = configargparse.ArgParser(default_config_files=config_files)
    parser.add_argument(
        '-cf', '--config', is_config_file=True, help='Configuration file')
    parser.add_argument(
        '-d', '--debug', help='Debug Mode', action='store_true', default=False)
    parser.add_argument(
        '-H', '--host', help='Set web server listening host',
        default='127.0.0.1')
    parser.add_argument(
        '-P', '--port', type=int,
        help='Set web server listening port', default=4000)
    parser.add_argument(
        '-C', '--concurrency', type=int,
        help='Maximum concurrent connections for the webserver.', default=200)
    parser.add_argument(
        '-m', '--manager_count', type=int, default=1,
        help='Number of Manager processes to start.')
    parser.add_argument(
        '-M', '--manager_name', type=parse_unicode,
        action='append', default=[],
        help='Names of Manager processes to start.')
    parser.add_argument(
        '-k', '--key', type=str, action='append', default=[],
        help='Specify a Google API Key to use.')
    parser.add_argument(
        '-f', '--filters', type=parse_unicode, action='append',
        default=['filters.json'],
        help='Filters configuration file. default: filters.json')
    parser.add_argument(
        '-a', '--alarms', type=parse_unicode, action='append',
        default=['alarms.json'],
        help='Alarms configuration file. default: alarms.json')
    parser.add_argument(
        '-gf', '--geofences', type=parse_unicode,
        action='append', default=[None],
        help='Alarms configuration file. default: None')
    parser.add_argument(
        '-l', '--location', type=parse_unicode, action='append',
        default=[None], help='Location, can be an address or coordinates')
    parser.add_argument(
        '-L', '--locale', type=parse_unicode, action='append', default=['en'],
        choices=['de', 'en', 'es', 'fr', 'it', 'ko', 'pt', 'zh_hk'],
        help='Locale for Pokemon and Move names: default en," '
             '+ " check locale folder for more options')
    parser.add_argument(
        '-u', '--units', type=parse_unicode, default=['imperial'],
        action='append', choices=['metric', 'imperial'],
        help='Specify either metric or imperial units to use for distance " '
             '+ "measurements. ')
    parser.add_argument(
        '-ct', '--cache_type', type=parse_unicode, action='append',
        default=['mem'], choices=cache_options,
        help="Specify the type of cache to use. Options: "
             + "['mem', 'file'] (Default: 'mem')")
    parser.add_argument(
        '-tl', '--timelimit', type=int, default=[0], action='append',
        help='Minimum limit')
    parser.add_argument(
        '-ma', '--max_attempts', type=int, default=[3], action='append',
        help='Maximum attempts an alarm makes to send a notification.')
    parser.add_argument(
        '-tz', '--timezone', type=str, action='append', default=[None],
        help='Timezone used for notifications. Ex: "America/Los_Angeles"')
    parser.add_argument(
        '-st', '--stations', type=str, default=[None], action='append',
        help='Should stations be included in alarms.')

    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('PokeAlarm').setLevel(logging.DEBUG)
        logging.getLogger('Manager').setLevel(logging.DEBUG)
        log.debug("Debug mode enabled!")

    config['HOST'] = args.host
    config['PORT'] = args.port
    config['CONCURRENCY'] = args.concurrency
    config['DEBUG'] = args.debug

    # Check to make sure that the same number of arguments are included
    for arg in [args.filters, args.alarms, args.geofences,
                args.location, args.locale, args.units, args.cache_type,
                args.timelimit, args.max_attempts,
                args.timezone, args.stations]:
        if len(arg) > 1:  # Remove defaults from the list
            arg.pop(0)
        size = len(arg)
        if size != 1 and size != args.manager_count:
            log.critical("Number of arguments must be either 1 for all "
                         + "managers or equal to Manager Count. Please "
                         + "provided the correct number of arguments.")
            log.critical(arg)
            sys.exit(1)

    # Attempt to parse the timezones
    for i in range(len(args.timezone)):
        if str(args.timezone[i]).lower() == "none":
            args.timezone[i] = None
            continue
        try:
            log.info(args.timezone[i])
            args.timezone[i] = pytz.timezone(args.timezone[i])
        except pytz.exceptions.UnknownTimeZoneError:
            log.error("Invalid timezone. For a list of valid timezones, see "
                      + "https://en.wikipedia.org/wiki"
                      + "/List_of_tz_database_time_zones")
            sys.exit(1)

    # Pad manager_name to match manager_count
    while len(args.manager_name) < args.manager_count:
        m_ct = len(args.manager_name)
        args.manager_name.append("Manager_{}".format(m_ct))

    # Build the managers
    for m_ct in range(args.manager_count):
        # TODO: Fix this mess better next time
        config['UNITS'] = get_from_list(args.units, m_ct, args.units[0])
        m = Manager(
            name=args.manager_name[m_ct],
            google_key=args.key,
            locale=get_from_list(args.locale, m_ct, args.locale[0]),
            units=get_from_list(args.units, m_ct, args.units[0]),
            timezone=get_from_list(args.timezone, m_ct, args.timezone[0]),
            time_limit=get_from_list(args.timelimit, m_ct, args.timelimit[0]),
            max_attempts=get_from_list(
                args.max_attempts, m_ct, args.max_attempts[0]),
            stations=get_from_list(
                args.stations, m_ct, args.stations[0]),
            quiet=False,  # TODO: I'll totally document this some day. Promise.
            cache_type=get_from_list(
                args.cache_type, m_ct, args.cache_type[0]),
            location=get_from_list(args.location, m_ct, args.location[0]),
            filter_file=get_from_list(args.filters, m_ct, args.filters[0]),
            geofence_file=get_from_list(
                args.geofences, m_ct, args.geofences[0]),
            alarm_file=get_from_list(args.alarms, m_ct, args.alarms[0]),
            debug=config['DEBUG']
        )
        if m.get_name() not in managers:
            # Add the manager to the map
            managers[m.get_name()] = m
        else:
            log.critical("Names of Manager processes must be unique "
                         + "(not case sensitive)! Process will exit.")
            sys.exit(1)
    log.info("Starting up the Managers")
    for m_name in managers:
        managers[m_name].start()

    # Set up signal handlers for graceful exit
    signal(signal.SIGINT, exit_gracefully)
    signal(signal.SIGTERM, exit_gracefully)


# Because lists are dumb and don't have a failsafe get
def get_from_list(arg, i, default):
    return arg[i] if len(arg) > 1 else default


def exit_gracefully():
    log.info("PokeAlarm is closing down!")
    server.stop()
    for m_name in managers:
        managers[m_name].stop()
    for m_name in managers:
        managers[m_name].join()
    log.info("PokeAlarm exited!")
    exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


if __name__ == '__main__':
    log.info("PokeAlarm is getting ready...")
    start_server()
