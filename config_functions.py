"""Common helper functions used by scripts to take values from config.json"""
import json
import datetime


def pick_hms(date):
    """Returns hours, minutes, seconds"""
    hours, minutes, seconds = map(int, date.split(':'))
    return hours, minutes, seconds


def get_config():
    """Returns consts defined in config.json"""
    with open('config.json', 'r') as config:
        ans = json.load(config)
        h, m, s = pick_hms(ans['collect_time'])
        ans['collect_time'] = datetime.timedelta(hours=h, minutes=m, seconds=s)
        h, m, s = pick_hms(ans['late_record'])
        ans['late_record'] = datetime.timedelta(hours=h, minutes=m, seconds=s)
        return ans
