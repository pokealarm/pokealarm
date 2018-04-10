#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Monkey Patch to allow Gevent's Concurrency
from datetime import timedelta, datetime

from gevent import monkey
monkey.patch_all()

# Standard Library Imports
import logging
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
from PokeAlarm.Utilities.Logging import setup_std_handler, setup_file_handler
from PokeAlarm.Cache import cache_options
from PokeAlarm.Manager import Manager
from PokeAlarm.Utils import get_path, parse_unicode, parse_boolean
from PokeAlarm.Load import parse_rules_file, parse_filters_file, \
    parse_alarms_file

# Reinforce UTF-8 as default
reload(sys)
sys.setdefaultencoding('UTF8')


log = logging.getLogger('pokealarm.webserver')

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
        data = json.loads(request.data)
        count = 1
        if type(data) == dict:  # older webhook style
            data_queue.put(data)
        else:   # For data set in frame
            count = len(data)
            for frame in data:
                data_queue.put(frame)
        log.debug("Received %s event(s) from %s.", count, request.remote_addr)
    except Exception as e:
        log.error("Encountered error while receiving webhook from %s: "
                  "(%s: %s)", request.remote_addr, type(e).__name__, e.message)
        # Send back 400
        abort(400)
    return "OK"


# Thread used to distribute the data into various processes
def manage_webhook_data(_queue):
    warning_limit = datetime.utcnow()
    while True:
        # Check queue length periodically
        if (datetime.utcnow() - warning_limit) > timedelta(seconds=30):
            warning_limit = datetime.utcnow()
            size = _queue.qsize()
            if size > 2000:
                log.warning("Queue length at %s! This may be causing a"
                            "significant delay in notifications.", size)
        # Distribute events to the other managers
        data = _queue.get(block=True)
        obj = Events.event_factory(data)
        if obj is None:  # TODO: Improve Event error checking
            continue
        for name, mgr in managers.iteritems():
            mgr.update(obj)
        log.debug("Distributed event %s to %s managers.",
                  obj.id, len(managers))


# Configure and run PokeAlarm
def start_server():
    # Parse Settings
    parse_settings(os.path.abspath(os.path.dirname(__file__)))

    # Start Webhook Manager in a Thread
    spawn(manage_webhook_data, data_queue)

    # Start up Server
    log.info("PokeAlarm is listening for webhooks on http://{}:{}"
             "".format(config['HOST'], config['PORT']))
    threads = pool.Pool(config['CONCURRENCY'])
    global server
    server = wsgi.WSGIServer(
        (config['HOST'], config['PORT']), app,
        log=logging.getLogger('webserver.internal'),
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

    # Webserver Settings:
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
        '-d', '--debug', action='store_true', default=False,
        help='Enable debuging mode.')
    parser.add_argument(
        '-q', '--quiet', action='store_true', default=False,
        help='Disables output to console.')
    parser.add_argument(
        '-ll', '--log-lvl', type=int, choices=[1, 2, 3, 4, 5], default=3,
        help='Verbosity of the root logger.')
    parser.add_argument(
        '-lf', '--log-file', type=parse_unicode, default='logs/pokealarm.log',
        help="Path of a file to attach to a manager's logger.")
    parser.add_argument(
        '-ls', '--log-size', type=int, default=100,
        help="Maximum size in mb of a log before rollover.")
    parser.add_argument(
        '-lc', '--log-ct', type=int, default=5,
        help="Maximum number of logs to keep.")

    # Manager Settings
    parser.add_argument(
        '-m', '--manager_count', type=int, default=1,
        help='Number of Manager processes to start.')
    parser.add_argument(
        '-M', '--manager_name', type=parse_unicode,
        action='append', default=[],
        help='Names of Manager processes to start.')
    parser.add_argument(
        '-mll', '--mgr-log-lvl', type=int, choices=[1, 2, 3, 4, 5],
        action='append', default=[3],
        help="Set the verbosity of a manager's logger.")
    parser.add_argument(
        '-mlf', '--mgr-log-file', type=parse_unicode,
        action='append', default=[None],
        help="Path of a file to attach to a manager's logger.")
    parser.add_argument(
        '-mls', '--mgr-log-size', type=int, action='append', default=[100],
        help="Maximum megabytes of a manager's log before rollover.")
    parser.add_argument(
        '-mlc', '--mgr-log-ct', type=int, action='append', default=[5],
        help="Maximum number of old manager's logs to keep before deletion.")
    # Files
    parser.add_argument(
        '-f', '--filters', type=parse_unicode, action='append',
        default=['filters.json'],
        help='Filters configuration file. default: filters.json')
    parser.add_argument(
        '-a', '--alarms', type=parse_unicode, action='append',
        default=['alarms.json'],
        help='Alarms configuration file. default: alarms.json')
    parser.add_argument(
        '-r', '--rules', type=parse_unicode, action='append',
        default=[None],
        help='Rules configuration file. default: None')
    parser.add_argument(
        '-gf', '--geofences', type=parse_unicode,
        action='append', default=[None],
        help='Alarms configuration file. default: None')

    # Location Specific
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
        '-tz', '--timezone', type=str, action='append', default=[None],
        help='Timezone used for notifications. Ex: "America/Los_Angeles"')

    # GMaps
    parser.add_argument(
        '-k', '--gmaps-key', type=parse_unicode, action='append',
        default=[None], help='Specify a Google API Key to use.')
    parser.add_argument(
        '--gmaps-rev-geocode', type=parse_boolean, action='append',
        default=[None], help='Enable Walking Distance Matrix DTS.')
    parser.add_argument(
        '--gmaps-dm-walk', type=parse_boolean, action='append',
        default=[None], help='Enable Walking Distance Matrix DTS.')
    parser.add_argument(
        '--gmaps-dm-bike', type=parse_boolean, action='append',
        default=[None], help='Enable Bicycling Distance Matrix DTS.')
    parser.add_argument(
        '--gmaps-dm-drive', type=parse_boolean, action='append',
        default=[None], help='Enable Driving Distance Matrix DTS.')
    parser.add_argument(
        '--gmaps-dm-transit', type=parse_boolean, action='append',
        default=[None], help='Enable Transit Distance Matrix DTS.')

    # Misc
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

    args = parser.parse_args()

    root_logger = logging.getLogger()
    if not args.quiet:
        setup_std_handler(root_logger)

    # Setup file logging
    if not os.path.exists(get_path('logs')):
        os.mkdir(get_path('logs'))
    setup_file_handler(root_logger, args.log_file, args.log_size, args.log_ct)

    if args.debug:
        # Set everything to VERY VERBOSE
        args.log_lvl = 5
        args.mgr_log_lvl = [5]
        log.info("Debug mode enabled!")

    logging.getLogger('webserver.internal').setLevel(logging.WARNING)
    # Set up webserver logging
    if args.log_lvl == 1:
        logging.getLogger('pokealarm.webserver').setLevel(logging.WARNING)
        logging.getLogger('pokealarm.setup').setLevel(logging.WARNING)
    elif args.log_lvl == 2:
        logging.getLogger('pokealarm.webserver').setLevel(logging.INFO)
        logging.getLogger('pokealarm.setup').setLevel(logging.WARNING)
    elif args.log_lvl == 3:
        logging.getLogger('pokealarm.webserver').setLevel(logging.INFO)
        logging.getLogger('pokealarm.setup').setLevel(logging.INFO)
    elif args.log_lvl == 4:
        logging.getLogger('pokealarm.webserver').setLevel(logging.INFO)
        logging.getLogger('pokealarm.setup').setLevel(logging.DEBUG)
    elif args.log_lvl == 5:
        logging.getLogger('pokealarm.webserver').setLevel(logging.DEBUG)
        logging.getLogger('pokealarm.setup').setLevel(logging.DEBUG)

    config['HOST'] = args.host
    config['PORT'] = args.port
    config['CONCURRENCY'] = args.concurrency
    config['DEBUG'] = args.debug

    # Check to make sure that the same number of arguments are included
    for arg in [args.gmaps_key, args.filters, args.alarms, args.rules,
                args.geofences, args.location, args.locale, args.units,
                args.cache_type, args.timelimit, args.max_attempts,
                args.timezone, args.gmaps_rev_geocode, args.gmaps_dm_walk,
                args.gmaps_dm_bike, args.gmaps_dm_drive,
                args.gmaps_dm_transit, args.mgr_log_lvl, args.mgr_log_size,
                args.mgr_log_file]:
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
        log.info("----------- Setting up 'manager_0'")
        config['UNITS'] = get_from_list(args.units, m_ct, args.units[0])
        m = Manager(
            name=args.manager_name[m_ct],
            google_key=get_from_list(
                args.gmaps_key, m_ct, args.gmaps_key[0]),
            locale=get_from_list(args.locale, m_ct, args.locale[0]),
            units=get_from_list(args.units, m_ct, args.units[0]),
            timezone=get_from_list(args.timezone, m_ct, args.timezone[0]),
            time_limit=get_from_list(args.timelimit, m_ct, args.timelimit[0]),
            max_attempts=get_from_list(
                args.max_attempts, m_ct, args.max_attempts[0]),
            cache_type=get_from_list(
                args.cache_type, m_ct, args.cache_type[0]),
            location=get_from_list(args.location, m_ct, args.location[0]),
            geofence_file=get_from_list(
                args.geofences, m_ct, args.geofences[0]),
            debug=config['DEBUG']
        )

        m.set_log_level(get_from_list(
            args.mgr_log_lvl, m_ct, args.mgr_log_lvl[0]))

        file_log = get_from_list(args.mgr_log_file, m_ct, args.mgr_log_file[0])
        if str(file_log).lower() != "none":
            size = get_from_list(args.mgr_log_size, m_ct, args.mgr_log_size[0])
            log_ct = get_from_list(args.mgr_log_ct, m_ct, args.mgr_log_ct[0])
            m.add_file_logger(file_log, size, log_ct)

        parse_filters_file(
            m, get_from_list(args.filters, m_ct, args.filters[0]))
        parse_alarms_file(
            m, get_from_list(args.alarms, m_ct, args.alarms[0]))
        parse_rules_file(m, get_from_list(args.rules, m_ct, args.rules[0]))

        # Set up GMaps stuff
        if get_from_list(
                args.gmaps_rev_geocode, m_ct, args.gmaps_rev_geocode[0]):
            m.enable_gmaps_reverse_geocoding()
        if get_from_list(args.gmaps_dm_walk, m_ct, args.gmaps_dm_walk[0]):
            m.enable_gmaps_distance_matrix('walking')
        if get_from_list(args.gmaps_dm_bike, m_ct, args.gmaps_dm_bike[0]):
            m.enable_gmaps_distance_matrix('biking')
        if get_from_list(args.gmaps_dm_drive, m_ct, args.gmaps_dm_drive[0]):
            m.enable_gmaps_distance_matrix('driving')
        if get_from_list(
                args.gmaps_dm_transit, m_ct, args.gmaps_dm_transit[0]):
            m.enable_gmaps_distance_matrix('transit')

        if m.get_name() not in managers:
            # Add the manager to the map
            managers[m.get_name()] = m
        else:
            log.critical("Names of Manager processes must be unique "
                         + "(not case sensitive)! Process will exit.")
            sys.exit(1)
        log.info("----------- Finished setting up 'manager_0'")
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
