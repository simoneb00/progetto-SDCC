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
def send_packet(packet, config):
    endpoint = config.get('api_gateway_upload_data')
    dictionary = convert_to_dict(packet)

    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(dictionary)
    r = requests.post(url=endpoint, data=json_data, headers=headers)
    return r.status_code, r.text


def query(city, country, date, full_data, only_national_average, config):
    endpoint = config.get('api_gateway_query')
    data = {
        'city': city,
        'country': country,
        'date': date,
        'full_data': full_data,
        'only_national_average': only_national_average
            }
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    r = requests.post(url=endpoint, data=json_data, headers=headers)
    return r.status_code, r.text
