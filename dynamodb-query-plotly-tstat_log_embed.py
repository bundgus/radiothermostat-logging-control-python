import boto3
import decimal
import json
from boto3.dynamodb.conditions import Key
import pandas as pd
import plotly.offline as offline
from plotly.graph_objs import *
from plotly import tools
import datetime
from pytz import timezone
from datetime import timedelta

hours_of_history = 24 * 2


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

response = table.query(
    ProjectionExpression="log_timestamp, ts1_tstate, ts2_tstate, ts1_temp, ts2_temp, "
                         "ts1_t_cool, ts2_t_cool, wu_temp_f, wu_relative_humidity",
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
            ProjectionExpression="log_timestamp, ts1_tstate, ts2_tstate, ts1_temp, ts2_temp, "
                                 "ts1_t_cool, ts2_t_cool, wu_temp_f, wu_relative_humidity",
            KeyConditionExpression=Key('tstat_id').eq('DEADBEEF')
                                   & Key('log_timestamp').gt(str(starttimestamp)),
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        df = df.append(pd.DataFrame(response['Items']))
    else:
        print('got all response pages')
        hasmorepages = False


state_ts2 = df['ts2_tstate'].copy()
state_ts2[df['ts2_tstate'] == 'Cool'] = 1
state_ts2[df['ts2_tstate'] == 'Off'] = 0
state_ts2[df['ts2_tstate'] == 'Heat'] = -1
state_ts1 = df['ts1_tstate'].copy()
state_ts1[df['ts1_tstate'] == 'Cool'] = 1
state_ts1[df['ts1_tstate'] == 'Off'] = 0
state_ts1[df['ts1_tstate'] == 'Heat'] = -1
df['log_timestamp'] = pd.to_datetime(df['log_timestamp'])

df['log_timestamp'] = df['log_timestamp'].dt.tz_localize('UTC') \
    .dt.tz_convert('US/Central').dt.tz_localize(None)

# plotting configuration follows:

fig = tools.make_subplots(rows=8, cols=1, print_grid=False, specs=[[{'rowspan': 6}],
                                                                   [None],
                                                                   [None],
                                                                   [None],
                                                                   [None],
                                                                   [None],
                                                                   [{}],
                                                                   [{}]
                                                                   ], shared_xaxes=True)

ts1_temp_trace = Scatter(
    x=df['log_timestamp'],
    y=df['ts1_temp'],
    name='ts1_temp',
    mode='markers',
    marker=dict(
        color='rgb(0, 255, 0)',
        size=5
    )
)

if 'ts1_t_heat' in df.columns:
    ts1_t_heat_trace = Scatter(
        x=df['log_timestamp'],
        y=df['ts1_t_heat'],
        name='ts1_t_heat',
        mode='lines',
        line=dict(
            color='rgb(255, 0, 0)',
            shape='hvh'
        )
    )
    fig.append_trace(ts1_t_heat_trace, 1, 1)

if 'ts1_t_cool' in df.columns:
    ts1_t_cool_trace = Scatter(
        x=df['log_timestamp'],
        y=df['ts1_t_cool'],
        name='ts1_t_cool',
        mode='lines',
        line=dict(
            color='rgb(0, 0, 255)',
            shape='hvh'
        )
    )
    fig.append_trace(ts1_t_cool_trace, 1, 1)

ts2_temp_trace = Scatter(
    x=df['log_timestamp'],
    y=df['ts2_temp'],
    name='ts2_temp',
    mode='markers',
    marker=dict(
        color='rgb(255, 128, 0)',
        size=5
    )
)

if 'ts2_t_heat' in df.columns:
    ts2_t_heat_trace = Scatter(
        x=df['log_timestamp'],
        y=df['ts2_t_heat'],
        name='ts2_t_heat',
        mode='lines',
        line=dict(
            color='rgb(255, 0, 255)',
            shape='hvh'
        )
    )
    fig.append_trace(ts2_t_heat_trace, 1, 1)

if 'ts2_t_cool' in df.columns:
    ts2_t_cool_trace = Scatter(
        x=df['log_timestamp'],
        y=df['ts2_t_cool'],
        name='ts2_t_cool',
        mode='lines',
        line=dict(
            color='rgb(0, 255, 255)',
            shape='hvh'
        )
    )
    fig.append_trace(ts2_t_cool_trace, 1, 1)

wu_temp_f_trace = Scatter(
    x=df['log_timestamp'],
    y=df['wu_temp_f'],
    name='wu_temp_f',
    mode='lines+markers',
    line=dict(
        color='rgb(0, 0, 0)',
        dash='dash',
        shape='spline'
    )
)

wu_relative_humidity_trace = Scatter(
    x=df['log_timestamp'],
    y=df['wu_relative_humidity'],
    name='wu_relative_humidity',
    yaxis='y2',
    mode='lines+markers',
    line=dict(
        dash='dash',
        shape='spline'
    )
)

state_ts1_trace = Scatter(
    x=df['log_timestamp'],
    y=state_ts1,
    name='state_ts1',
    # yaxis='y2',
    fill='tozeroy',
    line=dict(
        shape='hvh'
    )
)

state_ts2_trace = Scatter(
    x=df['log_timestamp'],
    y=state_ts2,
    name='state_ts2',
    # yaxis='y2',
    fill='tozeroy',
    line=dict(
        shape='hvh'
    )
)

fig.append_trace(wu_temp_f_trace, 1, 1)
fig.append_trace(ts1_temp_trace, 1, 1)
fig.append_trace(ts2_temp_trace, 1, 1)

fig.append_trace(state_ts2_trace, 7, 1)
fig.append_trace(state_ts1_trace, 8, 1)

fig['layout'].update(height=600, title='Temperatures and HVAC State ' + str(now))

div = offline.plot(fig, show_link=False, output_type='div', include_plotlyjs=False)

with open('plotly_embed.html', 'w') as pe:
    pe.write(div)