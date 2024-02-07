"""Checks the punctuality of Warsaw buses"""
import sys
import pandas as pd
from geopy.distance import geodesic
from .__helper_functions import get_data, plot_on_map, plot_histogram, create_time, pick_hms
from ..config_functions import get_config

config = get_config()
delays, stop_delay = [], {}


def convert_to_time(time_str):
    """Returns a tuple of (h, m, s) from string HH:MM:SS"""
    hours, minutes, seconds = map(int, time_str.split(':'))
    return create_time(hours % 24, minutes, seconds)


def drop_date(date):
    """Returns only time from string with date and time"""
    hours, minutes, seconds = pick_hms(date)
    return create_time(hours, minutes, seconds)


def get_stop_index(timetable, time_str):
    """Gets a stop which should be next for a bus"""
    hours, minutes, seconds = map(int, time_str.split(':'))
    # add some minutes in case bus is too early
    delta = config['punctuality_start_delta']
    hours, minutes = hours + (minutes + delta) // 60, (minutes + delta) % 60
    time_str = create_time(hours, minutes + 1, seconds)
    time_str = timetable.loc[timetable['time'] > time_str]
    if not time_str.empty:
        return time_str.index[0]
    return None


def closest_point(lat_point, lon_point, lat_line_start,
                  lon_line_start, lat_line_end, lon_line_end):
    """Finds distance between the point and a line"""
    line_v = [lat_line_end - lat_line_start, lon_line_end - lon_line_start]
    point_v = [lat_point - lat_line_start, lon_point - lon_line_start]
    s = sum(a ** 2 for a in line_v)
    if s != 0:
        p = max(0.0, min(1.0, sum(a * b for a, b in zip(point_v, line_v)) / s))
        closest_point_lat = lat_line_start + p * (lat_line_end - lat_line_start)
        closest_point_lon = lon_line_start + p * (lon_line_end - lon_line_start)
    else:
        closest_point_lat = lat_line_start
        closest_point_lon = lon_line_start
    return geodesic((lat_point, lon_point),
                    (closest_point_lat, closest_point_lon)).m


def check_brigade(data, table, brigade, line):
    """Checks punctuality of a given brigade"""
    table.index.name = 'idx'
    table = (table.loc[(table['line'] == line) & (table['brigade'] == brigade)].
             sort_values(by=['time', 'idx']).drop_duplicates().reset_index(drop=True))
    table['time'] = table['time'].apply(convert_to_time)
    data = (data.loc[(data['Lines'] == line) & (data['Brigade'] == brigade)].
            sort_values(by='Time').drop_duplicates().reset_index(drop=True))
    j = 0
    data['Time'] = data['Time'].apply(drop_date)
    i = get_stop_index(table, data['Time'][0])
    if i is None:
        return
    timetable_series = table.loc[i]
    location_series = data.loc[0]
    prev_lat, prev_lon = location_series['Lat'], location_series['Lon']
    s_dist = closest_point(timetable_series['Lat'], timetable_series['Lon'],
                           prev_lat, prev_lon,
                           location_series['Lat'], location_series['Lon'])
    while True:
        print('Record time: ' + location_series['Time'], file=sys.stderr)
        print('Next stop time: ' + timetable_series['time'], file=sys.stderr)
        cur_lat, cur_lon = location_series['Lat'], location_series['Lon']
        stop_lat, stop_lon = timetable_series['Lat'], timetable_series['Lon']
        dist = closest_point(stop_lat, stop_lon, prev_lat, prev_lon, cur_lat, cur_lon)
        if dist <= config['dist_from_stop']:
            print('Stop found!', file=sys.stderr)
            table_time = pd.to_timedelta(timetable_series['time'])
            actual_time = pd.to_timedelta(location_series['Time'])
            delay = (actual_time - table_time).total_seconds()
            if config['min_delay'] <= delay <= config['max_delay']:
                delays.append(delay / 60)  # else: value is unrealistic
                if (stop_lat, stop_lon) not in stop_delay:
                    stop_delay[(stop_lat, stop_lon)] = []
                stop_delay[(stop_lat, stop_lon)].append(delay / 60)
            i = i + 1
            if i == table.shape[0]:
                return
            timetable_series = table.loc[i]
            s_dist = closest_point(timetable_series['Lat'], timetable_series['Lon'],
                                   prev_lat, prev_lon, cur_lat, cur_lon)
        elif dist > config['far_from_stop'] and dist > 2 * s_dist:
            # we're far from stop and getting farther
            print('Skipping stop!', file=sys.stderr)
            i = get_stop_index(table, data['Time'][j])
            if i is None:
                return
            timetable_series = table.loc[i]
            s_dist = closest_point(timetable_series['Lat'], timetable_series['Lon'],
                                   prev_lat, prev_lon, cur_lat, cur_lon)
        else:
            print('Bus in move', file=sys.stderr)
            j = j + 1
            if j == data.shape[0]:
                return
            location_series = data.loc[j]
        if (location_series['Lat'], location_series['Lon']) != (cur_lat, cur_lon):
            prev_lat, prev_lon = cur_lat, cur_lon


def time():
    """Checks the punctuality of Warsaw buses"""
    ttable = pd.read_csv('timetable_coords.csv',
                         dtype={"brigade": str, "line": str})
    ddata, bus = get_data()
    tracked_buses = ddata[['Lines', 'Brigade']].drop_duplicates().reset_index(drop=True)
    for b in tracked_buses['Lines'].drop_duplicates():
        if bus not in ('', b):
            continue
        for brig in tracked_buses.loc[tracked_buses['Lines'] == b]['Brigade']:
            print(f'{b=}, {brig=}')
            check_brigade(ddata, ttable, brig, b)
    if bus != '':
        title = 'Delays of line ' + bus
    else:
        title = 'Delays of all lines'
    plot_histogram(delays, 'Delay', title)
    stop_map = {'Lat': [], 'Lon': [], 'Legend': []}
    for stop in stop_delay:
        stop_map['Lat'].append(stop[0])
        stop_map['Lon'].append(stop[1])
        stop_map['Legend'].append(round(sum(stop_delay[stop]) / len(stop_delay[stop]), 1))
    plot_on_map(pd.DataFrame(stop_map), 'Legend', 'Delay',
                'Average delay of Warsaw buses')
