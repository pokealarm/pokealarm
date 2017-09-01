# -*- coding: UTF-8 -*-
import json
import urllib2
import csv
import configargparse


def main():

    # ARGS
    parser = configargparse.ArgParser(description='geoFenceGen')
    parser.add_argument(
        '-dir',
        '--directory',
        help='Directory and filename of geofence. ex: geofence/Bratislava.txt',
        required=True)
    parser.add_argument(
        '-l',
        '--location',
        help='City/Country/area you would like a geofence for',
        required=True)

    parser.add_argument(
        '-w',
        '--way',
        help=('Use if there\'s no relational polygon' +
              '(ex: Manhattan central park'),
        action='store_true',
        default=False)
    parser.add_argument(
        '-mp',
        '--multiPolygon',
        help=('Use if you wish to write all polygons of an area'),
        action='store_true',
        default=False)
    args = parser.parse_args()
    loc = (args.location)
    loc = loc.replace(" ", "+")
    end = ("https://nominatim.openstreetmap.org/"
           "search.php?q='{}'&polygon_geojson=1&format=json".format(loc))

# Check for good response and get polygon

    if (len(json.load(urllib2.urlopen(end))) < 1):
        print 'Unable to find areas, exiting'
        exit(1)
    else:
        raw = json.load(urllib2.urlopen(end))
        mode = 'way' if (args.way) else 'relation'
        coords = [x for x in raw if x['osm_type'] ==
                  '{}'.format(mode)][0]['geojson']['coordinates']

# check if area has single polygon and write

    if (len(coords[0][0]) == 2 or (args.way)):
        # Write fenceFile
        l = [["{}".format(args.location)]]
        with open('{}'.format(args.directory), 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(l)
            for row in (coords[0]):
                writer.writerow(row[::-1])

        print(
            "Geofence of {} has been created in: {}".format(
                args.location,
                args.directory))

    else:
        # Write fenceFile or multiFence

        with open('{}'.format(args.directory), 'wb') as f:
            writer = csv.writer(f)
            mp = coords if (args.multiPolygon) else coords[0]
            n = 0
            for row in (mp):
                l = [["{} {}".format(args.location, n + 1)]]
                writer.writerow(l)
                for row in (coords[n][0]):
                    writer.writerow(row[::-1])
                n += 1
            print(
                "Geofence of {} has been created in: {}".format(
                    args.location, args.directory))


if __name__ == "__main__":
    main()
