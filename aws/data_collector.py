import json
import boto3
import botocore
import csv
from datetime import datetime


def create_csv(client, file_name, bucket_name):
    # check if file already exists
    try:
        response = client.get_object(Bucket=bucket_name, Key=file_name)
        return response['Body'].readlines()
    except botocore.exceptions.ClientError as e:
        # the file does not exist, return None
        return


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


def update_csv(prev_data, new_data, file_name, client, bucket_name):
    header = ['Name', 'Country', 'Temperature', 'Feels Like', 'Min Temperature', 'Max Temperature', 'Pressure',
              'Humidity', 'Date']

    if prev_data == None:
        with open(f"/tmp/{file_name}", 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerow(new_data)

    else:

        # prev_data != None, so it means the csv file already existed, so we need to extract the previous data

        data = format(prev_data)
        with open(f'/tmp/{file_name}', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data)
            writer.writerow(new_data)

    client.upload_file(f'/tmp/{file_name}', bucket_name, file_name)


def s3_persistence(data):
    s3_client = boto3.client('s3')
    s3 = boto3.resource('s3')

    bucket_name = "bucket-sdcc-" + data.get('country')

    s3_client.create_bucket(Bucket=bucket_name)
    response = create_csv(s3_client, data.get('country') + ".csv", bucket_name)
    update_csv(response, [data.get('name'),
                          data.get('country'),
                          data.get('temp'),
                          data.get('feels_like'),
                          data.get('temp_min'),
                          data.get('temp_max'),
                          data.get('pressure'),
                          data.get('humidity'),
                          data.get('date_time')],
               data.get('country') + '.csv',
               s3_client,
               bucket_name)


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
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            },
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
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            },
        ]
        )
        print(response)
    except dynamodb_client.exceptions.ResourceInUseException as e:
        # the table already exists, we can simply return None
        print('The table already exists')
        return


def put_data(dynamodb, data):

    string_date = data.get('date_time')     # iso formatted date
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

    #s3_persistence(data)
    dynamodb_persistence(data)

    return {
        'statusCode': 200,
        'body': json.dumps('Data correctly received.')
    }

