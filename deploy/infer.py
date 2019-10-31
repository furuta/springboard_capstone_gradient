import tensorflow as tf
from flask import Flask, jsonify, request
import pandas as pd
import dask
import dask.dataframe as dd
from argparse import ArgumentParser
import requests
from datetime import datetime
import time
import os
import jpholiday
from columns import ModelColumns
from schema import InputSchema
import json
import pickle
import math

# Parse input parameters
parser = ArgumentParser()
parser.add_argument("-m", "--model", dest="model",
                    help="location of the model")
parser.add_argument("-d", "--dataset", dest="dataset",
                    help="location of the dataset")
model_file = parser.parse_args().model
dataset_directory = parser.parse_args().dataset
model = tf.saved_model.load(model_file)

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
        inputs['holiday'] += [1 if jpholiday.is_holiday(dt.date()) else 0]
        df_inputs = pd.DataFrame(inputs)

    # df_inputs = pd.categorize(
    #     columns=['month', 'day_of_week', 'day'])  # need to categorize
    df_inputs = pd.get_dummies(
        df_inputs, columns=['month', 'day_of_week', 'day'])
    for column in modelColumns.get_input_columns():
        if not column in df_inputs:
            df_inputs[column] = 0
    # df_inputs = pd.DataFrame(columns=modelColumns.get_input_columns())
    # df_inputs = df_inputs.fillna(0)

    types = get_neighborhood_types(data['latitude'], data['longitude'])
    for t in types:
        column_name = 'neighborhood_' + t
        # add 1 if exitst neighborhood_{t}
        if column_name in df_inputs.columns:
            df_inputs[column_name] = df_inputs[column_name].map(lambda x: x+1)

    df_inputs['accommodates'] = data['accommodates']
    df_inputs['bedrooms'] = data['bedrooms']
    df_inputs['beds'] = data['beds']

    # if (room_type_column_name := get_room_type_column_name(data['room_type'])):# Python3.8~
    room_type_column_name = modelColumns.get_room_type_column_name(
        data['room_type'])
    if room_type_column_name:
        df_inputs[room_type_column_name] = 1

    # if (property_type_column_name := get_property_type_column_name(data['property_type'])):# Python3.8~
    property_type_column_name = modelColumns.get_property_type_column_name(
        data['property_type'])
    if property_type_column_name:
        df_inputs[property_type_column_name] = 1

    # if (cancellation_policy_column_name := get_cancellation_policy_column_name(data['cancellation_policy'])):# Python3.8~
    cancellation_policy_column_name = modelColumns.get_cancellation_policy_column_name(
        data['cancellation_policy'])
    if cancellation_policy_column_name:
        df_inputs[cancellation_policy_column_name] = 1

    ddf_inputs = dd.from_pandas(df_inputs, npartitions=4)
    prices_log = model(ddf_inputs)

    prices = []
    for i, price_log in enumerate(prices_log.numpy()):
        prices.append({
            "date": data['days_list'][i].strftime("%Y-%m-%d"),
            "price": math.e ** price_log[0]})

    # Return prices each date as JSON
    return jsonify(prices)


def get_neighborhood_types(latitude, longitude):
    types = []
    latitude_round = round(latitude, 4)
    longitude_round = round(longitude, 4)
    google_places_api_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
    language = 'en'

    neighborhood_data_filepath = dataset_directory + '/neighborhood' + RADIUS + '.pkl'
    if os.path.exists(neighborhood_data_filepath):
        df_neighborhood = pd.read_pickle(neighborhood_data_filepath)
    else:
        df_neighborhood = pd.DataFrame(
            [], columns=['latitude', 'longitude', 'types', 'created'])

    # find of neighborhood data
    neighborhood = df_neighborhood[(df_neighborhood['latitude'] == latitude_round) & (
        df_neighborhood['longitude'] == longitude_round)]

    # get only when there is no data
    if neighborhood.empty:
        print("!!!!!!!!!!!empty!!!!!!!!!!!")
        response = requests.get(google_places_api_url +
                                'key=' + API_KEY +
                                '&location=' + str(latitude_round) + ',' + str(longitude_round) +
                                '&radius=' + RADIUS +
                                '&language=' + language)
        data = response.json()
        for result in data['results']:
            types.append(result['types'][0])
        neighborhood = pd.DataFrame(
            [latitude_round, longitude_round, types, time.time()], index=df_neighborhood.columns).T
        df_neighborhood = df_neighborhood.append(neighborhood)

        with open(neighborhood_data_filepath, "wb") as target:
            pickle.dump(df_neighborhood, target)

    return neighborhood.at[0, 'types']


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
