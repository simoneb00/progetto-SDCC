"""
The following file contains the AWS Lambda functions
"""

import json
import boto3
import botocore
import csv
from datetime import datetime


# prev_data format: [header, b'Rome,it,28,28,23,32,50,50,2023-09-28\r\n', ...]
def format(prev_data):
    print('************ FORMATTING DATA **************')

    ret_list = []

    print(prev_data)

    for i in range(1, len(prev_data)):
        print(prev_data[i])

        # Remove the prefix "b'" and the suffix "'\r\n"
        data = prev_data[i].decode('utf-8')[0:-2]
        list = data.split(',')
        ret_list.append(list)

    print(ret_list)
    print('*****************************')
    return ret_list


def create_dynamodb_table(dynamodb_client, data):
    try:
        response = dynamodb_client.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'Name',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Date',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'Day',
                    'AttributeType': 'S'
                }
            ],
            TableName='table-sdcc-' + data.get('country'),
            KeySchema=[
                {
                    'AttributeName': 'Name',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'Date',
                    'KeyType': 'RANGE'
                }
            ],
            BillingMode='PAY_PER_REQUEST',
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'DayIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'Day',
                            'KeyType': 'HASH'
                        },
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        )
        print(response)
    except dynamodb_client.exceptions.ResourceInUseException as e:
        # the table already exists, we can simply return None
        print('The table already exists')
        return


def put_data(dynamodb, data):
    string_date = data.get('date_time')  # iso formatted date
    date_string = string_date[:10]
    time_string = string_date[11:]

    dynamodb.put_item(
        Item={
            'Name': {
                'S': data.get('name'),
            },
            'Country': {
                'S': data.get('country'),
            },
            'Temperature': {
                'N': str(data.get('temp')),
            },
            'Feels Like': {
                'N': str(data.get('feels_like')),
            },
            'Min Temperature': {
                'N': str(data.get('temp_min')),
            },
            'Max Temperature': {
                'N': str(data.get('temp_max')),
            },
            'Pressure': {
                'N': str(data.get('pressure')),
            },
            'Humidity': {
                'N': str(data.get('humidity')),
            },
            'Day': {
                'S': date_string,
            },
            'Time': {
                'S': time_string,
            },
            'Date': {
                'S': string_date,
            }
        },
        TableName='table-sdcc-' + data.get('country')
    )


def dynamodb_persistence(data):
    dynamodb_client = boto3.client('dynamodb')
    create_dynamodb_table(dynamodb_client, data)

    waiter = dynamodb_client.get_waiter('table_exists')
    waiter.wait(TableName='table-sdcc-' + data.get('country'))

    put_data(dynamodb_client, data)


def lambda_handler(event, context):
    data = json.loads(event['body'])

    print('received data for country ' + data.get('country').upper())

    dynamodb_persistence(data)

    return {
        'statusCode': 200,
        'body': json.dumps('Data correctly received.')
    }

