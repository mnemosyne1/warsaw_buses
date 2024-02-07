"""inititalises library"""
import datetime
import json
import os

default_config = {
	'collect_time': str(datetime.timedelta(hours=1, minutes=0, seconds=0)),
	'late_record': str(datetime.timedelta(hours=0, minutes=0, seconds=20)),
	'min_time_diff': 5,
	'speed_limit': 55,
	'max_plausible_speed': 90,
	'min_movement_speed': 10,
	'grid_precision': 3,
	'high_percent': 50,
	'punctuality_start_delta': 2,
	'dist_from_stop': 80,
	'min_delay': -300,
	'max_delay': 3600,
	'far_from_stop': 500,
	'highest_count': 1000,
	'now_timediff': 3
}
with open('config.json', 'w') as config:
	json.dump(default_config, config, indent=4)
if not os.path.exists('warszawa-dzielnice.geojson'):
	print('Remember to copy warszawa-dzielnice.geojson file!')
