import radiotherm
import datetime
import time
import requests
from datetime import timezone
import boto3
import decimal
import json

# include WU key in URL in file weather_underground_query_url.txt
# http://api.wunderground.com/api/<your key here>/conditions/q/<weather station here>.json
with open('weather_underground_query_url.txt', 'r') as f:
    wu_query_url = f.readline()

# 1st floor
IP1 = '192.168.0.111'
# 2ND floor
IP2 = '192.168.0.112'

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tstat_log')

while True:

    try:
        tstat_1 = radiotherm.get_thermostat(host_address=IP1)
        tstat_2 = radiotherm.get_thermostat(host_address=IP2)
    except Exception as e:
        print(e)
        print('unable to get connection to thermostat, retrying after 1 minute')
        time.sleep(60)  # Delay for 1 minute and try to reconnect
        continue

    while True:
        now = datetime.datetime.now(timezone.utc)

        try:
            # weather underground outside temp & weather conditions
            wu_r = requests.get(wu_query_url)
            parsed_json = wu_r.json()

            wu_temp_f = str(parsed_json['current_observation']['temp_f'])
            wu_relative_humidity = parsed_json['current_observation']['relative_humidity']
            wu_wind_degrees = parsed_json['current_observation']['wind_degrees']
            wu_wind_mph = str(parsed_json['current_observation']['wind_mph'])
            wu_wind_gust_mph = parsed_json['current_observation']['wind_gust_mph']
            wu_dewpoint_f = str(parsed_json['current_observation']['dewpoint_f'])
            wu_windchill_f = parsed_json['current_observation']['windchill_f']
            wu_heat_index_f = parsed_json['current_observation']['heat_index_f']
            wu_UV = parsed_json['current_observation']['UV']
            wu_precip_1hr_in = parsed_json['current_observation']['precip_1hr_in']
            wu_precip_today_in = parsed_json['current_observation']['precip_today_in']
            wu_weather = parsed_json['current_observation']['weather']

            # downstairs thermostat ts1 readings
            ts1_temp = str(tstat_1.temp['raw'])
            ts1_t_heat = str(tstat_1.t_heat['raw'])
            ts1_t_cool = str(tstat_1.t_cool['raw'])
            ts1_tmode = tstat_1.tmode['human']
            ts1_fmode = tstat_1.fmode['human']
            ts1_hold = tstat_1.hold['human']
            ts1_tstate = tstat_1.tstate['human']
            ts1_fstate = tstat_1.fstate['human']

            # upstairs thermostat ts1 readings
            ts2_temp = str(tstat_2.temp['raw'])
            ts2_t_heat = str(tstat_2.t_heat['raw'])
            ts2_t_cool = str(tstat_2.t_cool['raw'])
            ts2_tmode = tstat_2.tmode['human']
            ts2_fmode = tstat_2.fmode['human']
            ts2_hold = tstat_2.hold['human']
            ts2_tstate = tstat_2.tstate['human']
            ts2_fstate = tstat_2.fstate['human']

            sample = {'tstat_id': 'DEADBEEF',
                      'log_timestamp': str(now),
                      'ts1_tstat_name': '1st Floor',
                      'ts1_temp': ts1_temp,
                      'ts1_tmode': ts1_tmode,
                      'ts1_fmode': ts1_fmode,
                      'ts1_hold': ts1_hold,
                      'ts1_tstate': ts1_tstate,
                      'ts1_fstate': ts1_fstate,
                      'ts2_tstat_name': '2nd Floor',
                      'ts2_temp': str(ts2_temp),
                      'ts2_tmode': ts2_tmode,
                      'ts2_fmode': ts2_fmode,
                      'ts2_hold': ts2_hold,
                      'ts2_tstate': ts2_tstate,
                      'ts2_fstate': ts2_fstate,
                      'wu_station': 'pws:KTXARGYL24',
                      'wu_temp_f': wu_temp_f,
                      'wu_relative_humidity': wu_relative_humidity,
                      'wu_wind_degrees': wu_wind_degrees,
                      'wu_wind_mph': wu_wind_mph,
                      'wu_wind_gust_mph': wu_wind_gust_mph,
                      'wu_dewpoint_f': wu_dewpoint_f,
                      'wu_windchill_f': wu_windchill_f,
                      'wu_heat_index_f': wu_heat_index_f,
                      'wu_UV': wu_UV,
                      'wu_precip_1hr_in': wu_precip_1hr_in,
                      'wu_precip_today_in': wu_precip_today_in,
                      'wu_weather': wu_weather
                      }

            # declutter data by only logging the cool or heat settings if they apply to the current mode
            if ts1_tmode == 'Cool':
                sample['ts1_t_cool'] = ts1_t_cool
            if ts2_tmode == 'Cool':
                sample['ts2_t_cool'] = ts2_t_cool
            if ts1_tmode == 'Heat':
                sample['ts1_t_heat'] = ts1_t_heat
            if ts2_tmode == 'Heat':
                sample['ts2_t_heat'] = ts2_t_heat

            js = json.dumps(sample)
            print(js)

            table.put_item(Item=sample)

            time.sleep(300)  # Delay for 5 minutes (300 seconds)
        except Exception as e:
            print(e)
            print('getting new connection to thermostats')
            break
