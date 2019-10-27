import tensorflow as tf
from flask import Flask, jsonify, request
import pandas as pd
from sklearn.externals import joblib
from argparse import ArgumentParser
import requests
from datetime import datetime
import os
import jpholiday
from columns import ModelColumns
from schema import InputSchema
import json

# Parse input parameters
parser = ArgumentParser()
parser.add_argument("-m", "--model", dest="model",
                    help="location of the model")
model_file = parser.parse_args().model
# print(tf)
# model = tf.saved_model.load(os.path.dirname(
#     os.path.abspath(__file__)) + model_file)

# Read the EPOCH value from environment variable
API_KEY = os.getenv("API_KEY", '')
RADIUS = os.getenv("RADIUS", '300')

modelColumns = ModelColumns()
inputSchema = InputSchema()
app = Flask(__name__)


@app.route('/')
def index():
    return "Airbnb listing price prediction"


@app.route('/price', methods=['GET'])
def predict():
    errors = inputSchema.validate(request.args)
    if errors:
        return jsonify(errors)
    data, errors = inputSchema.dump(request.args)

    inputs = {'month': [], 'day': [], 'day_of_week': [], 'holiday': []}
    for dt in data['days_list']:
        inputs['month'] += [dt.month]
        inputs['day'] += [dt.day]
        inputs['day_of_week'] += [dt.weekday()]
        inputs['holiday'] += [jpholiday.is_holiday(dt.date())]
        df_inputs = pd.DataFrame(inputs)

    print(df_inputs)
    return 'test'
    # df_inputs = df_inputs.categorize(
    #     columns=['month', 'day_of_week', 'day'])  # need to categorize
    # df_inputs = dd.get_dummies(
    #     df_inputs, columns=['month', 'day_of_week', 'day'])
    # df_inputs = pd.DataFrame(columns=modelColumns.get_input_columns())
    # df_inputs = df_inputs.fillna(0)

    types = get_neighborhood_types(data['latitude'], data['longitude'])
    for t in types:
        # add 1 if exitst neighborhood_{t}
        df_inputs.loc['neighborhood_' + t] += 1

    df_inputs.loc['accommodates'] = data['accommodates']
    df_inputs.loc['bedrooms'] = data['bedrooms']
    df_inputs.loc['beds'] = data['beds']

    # if (room_type_column_name := get_room_type_column_name(data['room_type'])):# Python3.8~
    room_type_column_name = columns.get_room_type_column_name(
        data['room_type'])
    if room_type_column_name:
        df_inputs.loc[room_type_column_name] = 1

    # if (property_type_column_name := get_property_type_column_name(data['property_type'])):# Python3.8~
    property_type_column_name = columns.get_property_type_column_name(
        data['property_type'])
    if property_type_column_name:
        df_inputs.loc[property_type_column_name] = 1

    # if (cancellation_policy_column_name := get_cancellation_policy_column_name(data['cancellation_policy'])):# Python3.8~
    cancellation_policy_column_name = columns.get_cancellation_policy_column_name(
        data['cancellation_policy'])
    if cancellation_policy_column_name:
        df_inputs.loc[cancellation_policy_column_name] = 1

    y = model.predict(df_inputs)
    print(y)

    # Return prices each date as JSON
    return jsonify(y)


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
    app.run(host='localhost', port=8080)
