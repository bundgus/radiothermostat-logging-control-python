import boto3
import decimal
import json
from boto3.dynamodb.conditions import Key
import pandas as pd
import datetime
from pytz import timezone
from datetime import timedelta

hours_of_history = 24 * 180


# Helper class to convert a DynamoDB item to JSON.
# noinspection PyTypeChecker
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)


now = datetime.datetime.now(timezone('UTC'))
starttimestamp = now - timedelta(hours=hours_of_history)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('tstat_log')

pe = 'tstat_id, ' \
     'log_timestamp, ' \
     'ts1_tstat_name, ' \
     'ts1_temp, ' \
     'ts1_tmode, ' \
     'ts1_fmode, ' \
     'ts1_t_cool, ' \
     'ts1_t_heat, ' \
     'ts1_hold, ' \
     'ts1_tstate, ' \
     'ts1_fstate, ' \
     'ts2_tstat_name, ' \
     'ts2_temp, ' \
     'ts2_tmode, ' \
     'ts2_fmode, ' \
     'ts2_t_cool, ' \
     'ts2_t_heat, ' \
     'ts2_hold, ' \
     'ts2_tstate, ' \
     'ts2_fstate, ' \
     'wu_station, ' \
     'wu_temp_f, ' \
     'wu_relative_humidity, ' \
     'wu_wind_degrees, ' \
     'wu_wind_mph, ' \
     'wu_wind_gust_mph, ' \
     'wu_dewpoint_f, ' \
     'wu_windchill_f, ' \
     'wu_heat_index_f, ' \
     'wu_UV, ' \
     'wu_precip_1hr_in, ' \
     'wu_precip_today_in, ' \
     'wu_weather'

response = table.query(
    ProjectionExpression=pe,
    KeyConditionExpression=Key('tstat_id').eq('DEADBEEF')
                           & Key('log_timestamp').gt(str(starttimestamp))
)

df = pd.DataFrame(response['Items'])

# http://boto3.readthedocs.io/en/latest/reference/services/dynamodb.html#DynamoDB.Client.query
# If LastEvaluatedKey is present in the response, you will need to paginate the result set.
# For more information, see Paginating the Results in the Amazon DynamoDB Developer Guide .
hasmorepages = True

while hasmorepages:
    if 'LastEvaluatedKey' in response:
        print('LastEvaluatedKey', response['LastEvaluatedKey'])
        print('getting next page of results')
        response = table.query(
            ProjectionExpression=pe,
            KeyConditionExpression=Key('tstat_id').eq('DEADBEEF')
                                   & Key('log_timestamp').gt(str(starttimestamp)),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        df = df.append(pd.DataFrame(response['Items']))
    else:
        print('got all response pages')
        hasmorepages = False

print(df.to_csv('tstat_log.csv', index=False))
