# How to deploy
## Data Wrangling
```
gradient experiments run singlenode \
--name airbnb_data \
--projectId <ProjectID in gradient> \
--experimentEnv "{\"API_KEY\":\"<Google Maps Places API key>\",\"RADIUS\":300}" \
--container tensorflow/tensorflow:latest-gpu-py3 \
--machineType P4000 \
--command "pip install luigi jpholiday requests "dask[complete]" && python data/wrangling.py -o /storage/airbnb/dataset/marged_data.pkl" \
--modelType Tensorflow \
--workspaceUrl https://github.com/furuta/springboard_capstone_gradient
```

## Model Learning
```
gradient experiments run singlenode \
--name airbnb_model \
--projectId <ProjectID in gradient> \
--experimentEnv "{\"EPOCHS\":100,\"BATCH_SIZE\":500}" \
--container tensorflow/tensorflow:latest-gpu-py3 \
--machineType P4000 \
--command "pip install sklearn && pip install "dask[complete]" && python train/train_model.py -i /storage/airbnb/dataset/marged_data.pkl --modelPath /storage/airbnb/model --version 1" \
--modelType Tensorflow \
--modelPath "/storage/airbnb/model" \
--workspaceUrl https://github.com/furuta/springboard_capstone_gradient
```

## Deploy API
```
gradient jobs create \
--name deploy api \
--projectId <ProjectID in gradient> \
--jobEnv "{\"API_KEY\":\"<Google Maps Places API key>\",\"RADIUS\":300}" \
--container tensorflow/tensorflow:latest-py3 \
--machineType C3 \
--ports 8080:8080 \
--command "pip install flask jpholiday "dask[complete]" requests marshmallow && python deploy/infer.py -m /storage/airbnb/model/1 -d /storage/airbnb/dataset" \
--workspaceUrl https://github.com/furuta/springboard_capstone_gradient
```

*You can change the directories for data and model

# How to use API
### URL
http://{URL that the job in gradient made}/price

### Query Paramater
| key | type| required | detail |
|:---|:---:|:---:|:---|
|start |Date |YES |Set in YYYY-MM-DD format. This is the start date of the accommodation date for which you want to get a price. It must be in or after 2009. |
|end |Date |YES |Set in YYYY-MM-DD format. This is the last day of the accommodation date for which you want to get a price. It must be in or before 2029. |
|latitude |Float |YES |Set the latitude of the accommodation. It must be between 35.5014 and 35.8981 because learned data was Tokyo-to. |
|longitude |Float |YES |Set the longitude of the accommodation. It must be between 138.9257 and 139.9156 because learned data was Tokyo-to. |
|accommodates |Int |YES |Set the number of guests allowed. It must be a positive value. |
|bedrooms |Int |YES |Set the number of bedrooms. It must be a positive value. |
|beds |Int |YES |Set the number of beds. It must be a positive value. |
|room_type |Int |YES |Set the room type numerically.<br>1: room_type_Private room<br>2: room_type_Entire home/apt<br>3:room_type_Shared room |
|property_type |Int |YES |Set the accommodation type numerically.<br>1: property_type_Apartment<br>2: property_type_House<br>3: property_type_Serviced apartment<br>4: property_type_Condominium<br>5: property_type_Guest suite<br>6: property_type_Hut<br>7: property_type_Tiny house<br>8: property_type_Townhouse<br>9: property_type_Villa<br>10: property_type_Aparthotel<br>11: property_type_Cabin<br>12: property_type_Bed and breakfast<br>13: property_type_Loft<br>14: property_type_Hostel<br>15: property_type_Guesthouse<br>16: property_type_Boutique hotel<br>17: property_type_Nature lodge<br>18: property_type_Ryokan (Japan)<br>19: property_type_Tent<br>20: property_type_Hotel<br>21: property_type_Bungalow<br>22: property_type_Other<br>23: property_type_Camper/RV<br>24: property_type_Boat<br>25: property_type_Dome house<br>26: property_type_Dorm<br>27: property_type_Resort<br>28: property_type_Barn |
|cancellation_policy |Int |YES |Set the cancellation policy numerically.<br>1: cancellation_policy_strict_14_with_grace_period<br>2: cancellation_policy_moderate<br>3: cancellation_policy_flexible<br>4: cancellation_policy_super_strict_30<br>5: cancellation_policy_super_strict_60<br>6: cancellation_policy_strict |

### For Example
http://{URL that the job in gradient made}/price?start=2019-12-20&end=2019-12-30&latitude=35.67152&longitude=139.71203&accommodates=2&bedrooms=1&beds=2&room_type=1&property_type=2&cancellation_policy=1
