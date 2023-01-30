import plotly.express as px
import pandas as pd
import pymongo
import datetime
import numpy as np
from pandas.tseries.offsets import DateOffset
from bson.codec_options import CodecOptions
import pytz
from dash import Dash, html, dcc
from dash.dependencies import Input, Output

MONGO_CLIENT_STRING = ""
DATABASE_NAME = ""
COLLECTION_NAME = ""
TZ_OLSON_NAME = "Etc/UTC"

client = pymongo.MongoClient(MONGO_CLIENT_STRING)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME].with_options(codec_options=CodecOptions(
    tz_aware=True,
    tzinfo=pytz.timezone(TZ_OLSON_NAME)))
df = pd.DataFrame(list(collection.find().sort('timestamp',1))) #The df that is produced by default is sorted by player
df_server_uncontactable = pd.DataFrame(list(collection.find({'server_contactable':0})))
df_players_only = pd.DataFrame(list(collection.find({ 'player': { '$nin': ['No players online', None] } }))) #df produced is sorted by player

if df.empty:
    print('No data')
    exit(1)

def create_start_and_end_times(group, player_col_str):
    group['diff_min'] = group['timestamp'].diff().dt.total_seconds() / 60 #default is element in prev row

    # Set a threshold for new entry
    threshold = 5

    # Create a new column with a new entry if the difference is greater than the threshold
    group['new_entry'] = np.where(group['diff_min'] > threshold, 1, 0)

    # Create a new column with a cumulative sum of new entry
    group['group_id'] = group['new_entry'].cumsum() #every time new entry, cumsum incr

    # Group by group_id and find the start and end time
    result = group.groupby(['group_id'])['timestamp'].agg(['first','last']) #first and last are function names

    # Increase the timestamp in the last column by 5 minutes if the first and last are the same
    result['last'] =  result['last'] + DateOffset(minutes=5)

    #Create 'player' column, and add player name or 'script online'
    result = result.assign(player=player_col_str)
    
    #Convert groupby to df
    result = result.reset_index().drop('group_id', axis=1)

    return result

df_list = []

#Create dataframe of start and end times of the script - indicates if script was online (EXCEPT server uncontactable, but as of now it overlaps and the offline is on top)
#df_server_OK = df.drop(df[df.server_contactable == 0].index)
script_running_start_end = create_start_and_end_times(df, 'Script and server status')
script_running_start_end['key'] = 'Script was running'
df_list.append(script_running_start_end)

#Create dataframe of start and end times of when server is uncontactable
server_uncontactable_start_end = create_start_and_end_times(df_server_uncontactable, 'Script and server status')
server_uncontactable_start_end['key'] = 'Script running but Server uncontactable'
df_list.append(server_uncontactable_start_end)

#Create dataframe of start and end times of each player
if not df_players_only.empty:
    grouped_by_player = df_players_only.groupby('player') 
    for player, group in grouped_by_player:
        player_online_start_end = create_start_and_end_times(group, player)
        player_online_start_end['key'] = player_online_start_end['player']
        df_list.append(player_online_start_end)

#Combine all players into 1 df
timerange_df = pd.concat(df_list).reset_index(drop=True)

fig = px.timeline(timerange_df, x_start="first", x_end="last", y="player", color="key", hover_name='key')
fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
) 
fig.update_yaxes(autorange="reversed") # otherwise tasks are listed from the bottom up
fig.update_xaxes(rangeslider_visible=True, tickformat="%I:%M %p\n%a %b %e, %Y", minor=dict(ticks="inside", showgrid=True))

app = Dash(__name__)

app.layout = html.Div([

    dcc.Graph(
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)  # Turn off reloader if inside Jupyter