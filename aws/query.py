import json
import boto3
import botocore


def dict_list_to_float_list(dict_list):
    float_list = []
    for dict in dict_list:
        float_list.append(float(dict['N']))
    return float_list


# this function retrieves all data relative to the request's city
def get_data(city, country, date, only_national_average, full_data):
    filename = f'{country}-{date}.json'
    bucket_name = f'bucket-sdcc-{country}'
    client = boto3.client('s3')

    try:
        response = client.get_object(
            Bucket=bucket_name,
            Key=filename
        )

        file_json = json.load(response['Body'])

        if full_data == 1:
            return file_json
        if only_national_average == 1:
            return file_json.get('National Average')
        return file_json.get(city)

    except client.exceptions.NoSuchKey:
        # no data found
        return None


"""
Input example (json):
{
    'city': 'string',
    'country': 'string',
    'date': 'string',
    'full_data': 0/1,
    'only_national_average': 0/1
}

* city: name of the city, it can be None if only national average data or full_data is requested
* country: name of the country (ISO 3166-1 Alpha-2 code) [REQUIRED]
* date: date of the requested average data (YYYY-MM-DD) [REQUIRED]
* full_data: 0/1 value, if equals to 1 it specifies that all data is requested (all cities and national average, 
  oth. only national average or one city) [REQUIRED] 
* only_national_average: 0/1 value, if equals to 1 it specifies that only national average data is requested [REQUIRED]
"""


def lambda_handler(event, context):
    data = json.loads(event['body'])

    if ('city' not in data) and ((data['only_national_average'] == 0) and (data['full_data'] == 0)):
        return {
            'statusCode': 400,
            'body': json.dumps('No city specified and no national avg data or full data requested.')
        }
    if ('country' not in data) or ('date' not in data) or ('full_data' not in data) or (
            'only_national_average' not in data):
        return {
            'statusCode': 400,
            'body': json.dumps('Missing information in input')
        }
    if (data['full_data'] != 0) and (data['full_data'] != 1):
        return {
            'statusCode': 400,
            'body': json.dumps('full_data must be either 0 or 1')
        }
    if (data['only_national_average'] != 0) and (data['only_national_average'] != 1):
        return {
            'statusCode': 400,
            'body': json.dumps('full_data must be either 0 or 1')
        }

    return_data = get_data(
        data['city'],
        data['country'],
        data['date'],
        data['only_national_average'],
        data['full_data']
    )

    if return_data is None:
        return {
            'statusCode': 404,
            'body': 'No data available.'
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(return_data)
        }
