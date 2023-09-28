"""
This file contains all the functions realised to communicate with AWS
"""
import json

import requests


def convert_to_dict(packet):
    data = {'name': packet.name,
            'country': packet.country,
            'temp': packet.temp,
            'feels_like': packet.feels_like,
            'temp_min': packet.temp_min,
            'temp_max': packet.temp_max,
            'pressure': packet.pressure,
            'humidity': packet.humidity,
            'date_time': packet.date_time.strftime("%Y-%m-%d %H:%M:%S")
            }
    return data


# this function sends a json file to the API trigger for the AWS Lambda function
def send_packet(packet):
    endpoint = "https://e1b792l8l1.execute-api.us-east-1.amazonaws.com/default/cloudWeatherDataCollector"  # todo add conf file
    dict = convert_to_dict(packet)

    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(dict)
    print(json_data)
    r = requests.post(url=endpoint, data=json_data, headers=headers)
    return r.status_code, r.text

