# Endpoint is gSt: converts point ([lat,lng]) into string (closest station within 500m or None)

# Benchmarks (first 1000 points) (secs):
# PYTHON geopy vicenty:                 35.5
# PYTHON geopy great_circle:            20.5
# PYTHON turf.js [port] (great circle): 10.5
# JAVASCRIPT turf.js (great circle):    0.7

import json
import io

with io.open('data/stations.json', encoding='utf8', errors='ignore') as file: stations = json.load(file)['features']

def flip(point): return [point[1], point[0]]

# geopy distance module
# from geopy.distance import <great_circle OR vincenty> as geopyDistance
# def geopyDistance(point1, point2): return geopyDistance(point1, point2).kilometers

# turf.js ported distance module
import math
def distance(point1, point2):
    degrees2radians = math.pi / 180
    dLat = degrees2radians * (point2[0] - point1[0])
    dLon = degrees2radians * (point2[1] - point1[1])
    lat1 = degrees2radians * point1[0]
    lat2 = degrees2radians * point2[0]
    a = math.pow(math.sin(dLat / 2), 2) + math.pow(math.sin(dLon / 2), 2) * math.cos(lat1) * math.cos(lat2)
    return (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))) * 6373

def closestPoint(point, pointArray, distanceCap=10000):
    closestDistance = distanceCap
    closestName = None
    for testPoint in pointArray:
        testDistance = distance(point, flip(testPoint['geometry']['coordinates']))
        if testDistance < closestDistance:
            closestDistance = testDistance
            closestName = testPoint['properties']['name']
    return closestName

def gSt(point): return closestPoint(point, stations, 0.5)
