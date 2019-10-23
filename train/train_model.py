import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
import numpy as np
import os
import argparse
import pickle
import dask
import dask.dataframe as dd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.wrappers.scikit_learn import KerasRegressor
from tensorflow.keras import backend as K
# from keras.layers import Dropout
# from keras.optimizers import Adam
# from keras.callbacks import EarlyStopping

# tf.logging.set_verbosity(tf.logging.ERROR)

# Parse input parameters
parser = argparse.ArgumentParser(description='Airbnb Listing Keras Model')
parser.add_argument('--modelPath', type=str, dest='MODEL_DIR',
                    help='location to store the model artifacts')
parser.add_argument('--version', type=str, dest='VERSION',
                    default="1", help='model version')
parser.add_argument("-i", "--in", dest="input",
                    help="location of input dataset")
args = parser.parse_args()

MODEL_DIR = args.MODEL_DIR
VERSION = args.VERSION
INPUT_FILE = args.input


def r2_keras(y_true, y_pred):
    SS_res = K.sum(K.square(y_true - y_pred))
    SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
    return (1 - SS_res/(SS_tot + K.epsilon()))


# Load data
with open(INPUT_FILE, 'rb') as f:
    ddf_airbnb = pickle.load(f)
print(ddf_airbnb.head())

ddf_airbnb = ddf_airbnb.dropna()
ddf_airbnb['price_amount_log'] = np.log(ddf_airbnb['price_amount'])
del ddf_airbnb['price_amount']

y = ddf_airbnb['price_amount_log']
X = ddf_airbnb.drop('price_amount_log', axis=1)
X_train, X_val, y_train, y_val = train_test_split(
    X, y, train_size=0.8, test_size=0.2, random_state=1)


# Build model
model = Sequential()
model.add(Dense(91, input_dim=91, kernel_initializer='normal', activation='relu'))
model.add(Dense(50, kernel_initializer='normal', activation='relu'))
model.add(Dense(30, kernel_initializer='normal', activation='relu'))
model.add(Dense(30, kernel_initializer='normal', activation='relu'))
model.add(Dense(30, kernel_initializer='normal', activation='relu'))
model.add(Dense(1, kernel_initializer='normal'))
model.summary()

# Read the EPOCH value from environment variable
epochs = int(os.getenv("EPOCHS", 300))
batch_size = int(os.getenv("BATCH_SIZE", 500))

#Compile and fit
model.compile(loss=['mean_squared_error'], metrics=[
              r2_keras], optimizer='Adam')

# estimator = KerasRegressor(
#     build_fn=model, batch_size=batch_size, verbose=0)
# estimator.fit(X_train, y_train, epochs=epochs, validation_split=0.2)
model.fit(X_train, y_train, epochs=epochs,
          validation_split=0.2, batch_size=batch_size)
# Check accuracy
test_loss, test_r2 = model.evaluate(X_val, y_val)
print('\nModel loss: {}'.format(test_loss))
print('\nModel r2: {}'.format(test_r2))

# Save model
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)
    export_path = os.path.join(MODEL_DIR, VERSION)
    print('export_path = {}\n'.format(export_path))

    tf.saved_model.simple_save(
        tf.backend.get_session(),
        export_path,
        inputs={'input_image': model.input},
        outputs={t.name: t for t in model.outputs})

    print('\nModel saved to ' + MODEL_DIR)
else:
    print('\nExisting model found at ' + MODEL_DIR)
    print('\nDid not overwrite old model. Run the job again with a different location to store the model')


# import numpy as np
# # import pandas as pd
# import pickle
# import dask
# import dask.dataframe as dd
# # from pandas import Series,DataFrame
# from keras.models import Sequential
# from keras.layers import Dense
# # from sklearn.metrics import r2_score
# from sklearn.preprocessing import StandardScaler
# # from sklearn.pipeline import Pipeline
# # from livelossplot.keras import PlotLossesCallback
# from keras import backend as K
# from keras.layers import Dropout
# from keras.optimizers import Adam
# from keras.callbacks import EarlyStopping
