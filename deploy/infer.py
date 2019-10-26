from flask import Flask, jsonify, request
import pandas as pd
from sklearn.externals import joblib
from argparse import ArgumentParser
import requests
from datetime import datetime as dt
from datetime import timedelta
import os
import jpholiday
import columns

# Parse input parameters
parser = ArgumentParser()
parser.add_argument("-m", "--model", dest="model",
                    help="location of the model")
model_file = parser.parse_args().model
loaded_model = joblib.load(model_file)

# Read the EPOCH value from environment variable
API_KEY = os.getenv("API_KEY", '')
RADIUS = os.getenv("RADIUS", '300')

app = Flask(__name__)


@app.route('/')
def index():
    return "Airbnb listing price prediction"


@app.route('/price', methods=['GET'])
def predict():
    df_inputs = pd.DataFrame(columns=columns.input_columns)
    df_inputs = df_inputs.fillna(0)

    fromDate = request.args.get('from')
    toDate = request.args.get('to')
    # Todo:replace / to -
    fromdt = dt.strptime(fromDate, '%Y-%m-%d')
    todt = dt.strptime(toDate, '%Y-%m-%d')
    # Todo:From 2009
    # Todo:Until 2029
    days_num = (todt - fromdt).days + 1
    # Todo:Up to 365
    # for i in range(days_num):
    # datelist.append(strdt + timedelta(days=i))
    # tmp_se = pd.Series([i, i*i], index=list_df.columns)
    # list_df = list_df.append(tmp_se, ignore_index=True)

    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    types = get_neighborhood_types(latitude, longitude)
    for type in types:
        # add 1 if exitst neighborhood_{type}
        df_inputs.loc['neighborhood_' + type] += 1

    accommodates = request.args.get('accommodates')
    df_inputs.loc['accommodates'] = accommodates
    bedrooms = request.args.get('bedrooms')
    df_inputs.loc['bedrooms'] = bedrooms
    beds = request.args.get('beds')
    df_inputs.loc['beds'] = beds

    room_type = request.args.get('room_type')
    # if (room_type_column_name := get_room_type_column_name(room_type)):# Python3.8~
    room_type_column_name = columns.get_room_type_column_name(room_type)
    if room_type_column_name:
        df_inputs.loc[room_type_column_name] = 1

    property_type = request.args.get('property_type')
    # if (property_type_column_name := get_property_type_column_name(property_type)):# Python3.8~
    property_type_column_name = columns.get_property_type_column_name(
        property_type)
    if property_type_column_name:
        df_inputs.loc[property_type_column_name] = 1

    cancellation_policy = request.args.get('cancellation_policy')
    # if (cancellation_policy_column_name := get_cancellation_policy_column_name(property_type)):# Python3.8~
    cancellation_policy_column_name = columns.get_cancellation_policy_column_name(
        cancellation_policy)
    if cancellation_policy_column_name:
        df_inputs.loc[cancellation_policy_column_name] = 1

    y = loaded_model.predict(df_inputs)
    print(y)

    # Return prices each date as JSON
    return 'test'


def get_neighborhood_types(latitude, longitude):
    types = []
    latitude_round = round(latitude, 4)
    longitude_round = round(longitude, 4)
    google_places_api_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    language = 'en'
    response = requests.get(google_places_api_url +
                            'key=' + API_KEY +
                            '&location=' + str(latitude_round) + ',' + str(longitude_round) +
                            '&radius=' + RADIUS +
                            '&language=' + language)
    data = response.json()

    # for result in data['results']:
    #     types.append(result['types'][0])
    # neighborhood = pd.DataFrame(
    #     [latitude_round, longitude_round, types, time.time()], index=df_neighborhood.columns).T
    # df_neighborhood = df_neighborhood.append(neighborhood)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
