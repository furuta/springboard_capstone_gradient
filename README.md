# How to use
## For data wrangling
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

## For model learning
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

## For deploy API
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
