# Simulation of a distributed sensor network in the edge-cloud continuum
This simple application simulates a distributed sensor network. It contains the following components:
* Sensors: source of weather data (simulated via api from OpenWeatherMap).
* Edge devices: Docker containers that perform data conversions and send data to the cloud.
* Cloud: AWS services, i.e. Lambda functions that collect data from API Gateways and save it into DynamoDB tables. Once a day, average statistics are computed for the previous day and saved on a S3 bucket. 