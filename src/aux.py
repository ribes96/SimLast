#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
from pprint import pprint

stationsFile = 'topology/stations'
paramsFile = 'params/params'

stations = []
params = {}

# reads the positions of the stations and initialize all the stations
def readStations():
    global stations
    f = open(stationsFile, 'r')
    postrings = list(f)
    station_positions = list(map(int, postrings))
    station_positions.sort()
    for num in station_positions:
        stat = {}
        stat['pos'] = num
        stat['people'] = []
        stat['buses'] = []
        stations.append(stat)
    f.close()

def readParams():
    global params
    with open(paramsFile) as data_file:
        params = json.load(data_file)
    # pprint(params)
