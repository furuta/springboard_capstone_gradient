import pandas as pd
import numpy as np
import dask
import dask.dataframe as dd
import jpholiday
import luigi
import pickle
import datetime
import time
import requests
import json
import os
import argparse

# Parse input parameters
parser = argparse.ArgumentParser(description='Airbnb Listing Data Wrangling')
parser.add_argument("-o", "--out", dest="output",
                    help="location of output dataset")
args = parser.parse_args()

OUTPUT_FILE = args.output

# Read the EPOCH value from environment variable
API_KEY = os.getenv("API_KEY", '')
RADIUS = os.getenv("RADIUS", '300')


class ModifyCalendarDataTask(luigi.Task):
    calendar_csv_filename = luigi.Parameter()
    modified_calendar_filename = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.modified_calendar_filename)

    def run(self):
        start_time = datetime.now()
        print("================================================")
        print("==========Start ModifyCalendarDataTask==========")
        dtype={'maximum_nights': 'float64', 'minimum_nights': 'float64'}
        ddf_calendar = dd.read_csv(self.calendar_csv_filename, dtype=dtype)

        use_columns_in_calendar = [
            'listing_id',
            'date',
            'price',
        ]
        ddf_calendar = ddf_calendar.loc[:, use_columns_in_calendar]
        ddf_calendar = ddf_calendar.dropna()
        print(ddf_calendar.head())

        # price
        ddf_calendar['price_amount'] = ddf_calendar['price'].map(lambda x: int(float(
            str(x).replace(',', '').replace('$', ''))), meta=('x', int))  # need to specify type

        # date
        ddf_calendar['datetime'] = ddf_calendar['date'].map(lambda x: datetime.datetime.strptime(
            str(x), '%Y-%m-%d'), meta=('x', object))  # need to specify type
        ddf_calendar['month'] = ddf_calendar['datetime'].map(
            lambda x: x.month, meta=('x', int))  # need to specify type
        ddf_calendar['day'] = ddf_calendar['datetime'].map(
            lambda x: x.day, meta=('x', int))  # need to specify type
        ddf_calendar['day_of_week'] = ddf_calendar['datetime'].map(
            lambda x: x.weekday(), meta=('x', int))  # need to specify type
        ddf_calendar['holiday'] = ddf_calendar['datetime'].map(lambda x: 1 if jpholiday.is_holiday(
            x.date()) else 0, meta=('x', int))  # need to specify type
        ddf_calendar = ddf_calendar.categorize(
            columns=['month', 'day_of_week', 'day'])  # need to categorize
        ddf_calendar = dd.get_dummies(
            ddf_calendar, columns=['month', 'day_of_week', 'day'])

        del ddf_calendar['date']
        del ddf_calendar['price']
        del ddf_calendar['datetime']
        ddf_calendar = ddf_calendar.compute()

        print(ddf_calendar.head())
        print(ddf_calendar.shape)
        print(ddf_calendar.columns)
        with open(self.output().path, "wb") as target:
            pickle.dump(ddf_calendar, target)

        print("==========End ModifyCalendarDataTask==========")
        print("==============================================")
        print("Time ", datetime.now() - start_time)


class ModifyListingDataTask(luigi.Task):
    listings_csv_filename = luigi.Parameter()
    modified_listings_filename = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(self.modified_listings_filename)

    def run(self):
        start_time = datetime.now()
        print("===============================================")
        print("==========Start ModifyListingDataTask==========")
        dtype = {'bedrooms': 'float32',
                 'beds': 'float32',
                 'review_scores_accuracy': 'float32',
                 'review_scores_checkin': 'float32',
                 'review_scores_cleanliness': 'float32',
                 'review_scores_communication': 'float32',
                 'review_scores_location': 'float32',
                 'review_scores_rating': 'float32',
                 'review_scores_value': 'float32'}
        ddf_listing = dd.read_csv(self.listings_csv_filename, dtype=dtype)

        use_columns_in_listing = [
            'id',
            'latitude',
            'longitude',
            'property_type',
            'room_type',
            'accommodates',
            'bedrooms',
            'beds',
            'cancellation_policy',
        ]
        ddf_listing = ddf_listing.loc[:, use_columns_in_listing]
        print(ddf_listing.head())

        # property_type, room_type, cancellation_policy
        ddf_listing = ddf_listing.categorize(
            columns=['property_type', 'room_type', 'cancellation_policy'])
        ddf_listing = dd.get_dummies(
            ddf_listing, columns=['property_type', 'room_type', 'cancellation_policy'])

        # ddf_listing = ddf_listing.reset_index()
        ddf_listing = ddf_listing.rename(columns={'id': 'listing_id'})
        ddf_listing = ddf_listing.compute()

        print(ddf_listing.head())
        print(ddf_listing.shape)
        print(ddf_listing.columns)
        with open(self.output().path, "wb") as target:
            pickle.dump(ddf_listing, target)

        print("==========End ModifyListingDataTask==========")
        print("=============================================")
        print("Time ", datetime.now() - start_time)


class MargeNeighborhoodDataTask(luigi.Task):
    neighborhood_data_file = luigi.Parameter()
    modified_listings_filename = luigi.Parameter()
    modified_listings_with_neighborhood_filename = luigi.Parameter()
    google_places_api_url = luigi.Parameter()
    language = 'en'

    def requires(self):
        return ModifyListingDataTask()

    def output(self):
        return luigi.LocalTarget(self.modified_listings_with_neighborhood_filename)

    def run(self):
        start_time = datetime.now()
        print("===================================================")
        print("==========Start MargeNeighborhoodDataTask==========")
        # TODO:This should be managed with DB
        neighborhood_data_filepath = self.neighborhood_data_file + RADIUS + '.pkl'
        if os.path.exists(neighborhood_data_filepath):
            df_neighborhood = pd.read_pickle(neighborhood_data_filepath)
        else:
            df_neighborhood = pd.DataFrame(
                [], columns=['latitude', 'longitude', 'types', 'created'])

        df_listing = pd.read_pickle(self.modified_listings_filename)

        count = 1
        for index, row in df_listing.iterrows():
            # Because the difference is less than 10m, round off to the four decimal places
            latitude_round = round(row.latitude, 4)
            longitude_round = round(row.longitude, 4)

            # find of neighborhood data
            neighborhood = df_neighborhood[(df_neighborhood['latitude'] == latitude_round) & (
                df_neighborhood['longitude'] == longitude_round)]

            # get only when there is no data
            if neighborhood.empty:
                print("[{}]!!!!!!!!!!!empty!!!!!!!!!!!".format(count))
                # if not exist, get data from api
                response = requests.get(self.google_places_api_url +
                                        'key=' + API_KEY +
                                        '&location=' + str(latitude_round) + ',' + str(longitude_round) +
                                        '&radius=' + RADIUS +
                                        '&language=' + self.language)
                data = response.json()

                types = []
                for result in data['results']:
                    types.append(result['types'][0])
                neighborhood = pd.DataFrame(
                    [latitude_round, longitude_round, types, time.time()], index=df_neighborhood.columns).T
                df_neighborhood = df_neighborhood.append(neighborhood)

                with open(neighborhood_data_filepath, "wb") as target:
                    pickle.dump(df_neighborhood, target)
            # else:
                # print("[{}]-----------exist-----------".format(count))
            count += 1

            for neighbor_type in neighborhood.at[0, 'types']:
                column_name = 'neighborhood_' + neighbor_type
                if not column_name in df_listing.columns:
                    df_listing[column_name] = 0
                df_listing.loc[index, column_name] += 1

        del df_listing['latitude']
        del df_listing['longitude']
        ddf_listing = dd.from_pandas(df_listing, npartitions=4)

        print(df_listing.head())
        print(df_listing.shape)
        print(df_listing.columns)
        with open(self.output().path, "wb") as target:
            pickle.dump(df_listing, target)

        print("==========End MargeNeighborhoodDataTask==========")
        print("=================================================")
        print("Time ", datetime.now() - start_time)


class MargeAndPrepareDataTask(luigi.Task):
    modified_calendar_filename = luigi.Parameter()
    modified_listings_with_neighborhood_filename = luigi.Parameter()

    def requires(self):
        return [ModifyCalendarDataTask(), MargeNeighborhoodDataTask()]

    def output(self):
        return luigi.LocalTarget(OUTPUT_FILE)

    def run(self):
        start_time = datetime.now()
        print("=================================================")
        print("==========Start MargeAndPrepareDataTask==========")
        with open(self.modified_calendar_filename, 'rb') as f:
            ddf_calendar = pickle.load(f)
        with open(self.modified_listings_with_neighborhood_filename, 'rb') as f:
            ddf_listing = pickle.load(f)
        ddf_marged = ddf_calendar.merge(ddf_listing, on='listing_id')
        del ddf_marged['listing_id']
        ddf_marged = ddf_marged.dropna()
        # ddf_marged = ddf_marged.compute()

        print(ddf_marged.head())
        print(ddf_marged.shape)
        print(ddf_marged.columns)
        with open(self.output().path, "wb") as target:
            pickle.dump(ddf_marged, target)

        print("==========End MargeAndPrepareDataTask==========")
        print("===============================================")
        print("Time ", datetime.now() - start_time)


if __name__ == '__main__':
    # luigi.run(['ModifyCalendarDataTask', '--workers', '1', '--local-scheduler'])
    # luigi.run(['ModifyListingDataTask', '--workers', '1', '--local-scheduler'])
    # luigi.run(['MargeNeighborhoodDataTask','--workers', '1', '--local-scheduler'])
    luigi.run(['MargeAndPrepareDataTask', '--workers', '1', '--local-scheduler'])

# luigid --background --pidfile ./tmp/pidfile --logdir ./luigi_log --state-path ./tmp/state
