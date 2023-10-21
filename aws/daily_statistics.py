import json
import boto3
import botocore
from datetime import datetime, timedelta


class Statistics:
    def __init__(self, city, country, temp, feels_like, temp_min, temp_max, pressure, humidity):
        self.city = city
        self.country = country
        self.temp = temp
        self.feels_like = feels_like
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.pressure = pressure
        self.humidity = humidity


def query(client, date, table_name):
    response = client.query(
        TableName=table_name,
        IndexName='DayIndex',
        ExpressionAttributeValues={
            ':v1': {
                'S': date
            }
        },
        ExpressionAttributeNames={"#day": "Day"},
        KeyConditionExpression='#day = :v1'
    )

    return response['Count'] > 1


def compute_mean_statistics(all_statistics):
    statistics = {}

    for stat in all_statistics:
        if str(stat.city) in statistics.keys():
            statistics[str(stat.city)]["temp"].append(stat.temp)
            statistics[str(stat.city)]["feels_like"].append(stat.feels_like)
            statistics[str(stat.city)]["temp_min"].append(stat.temp_min)
            statistics[str(stat.city)]["temp_max"].append(stat.temp_max)
            statistics[str(stat.city)]["pressure"].append(stat.pressure)
            statistics[str(stat.city)]["humidity"].append(stat.humidity)
        else:
            statistics[str(stat.city)] = {
                "temp": [stat.temp],
                "feels_like": [stat.feels_like],
                "temp_min": [stat.temp_min],
                "temp_max": [stat.temp_max],
                "pressure": [stat.pressure],
                "humidity": [stat.humidity],
            }

    avg_statistics = {}
    all_temp = []
    all_feels_like = []
    all_temp_min = []
    all_temp_max = []
    all_pressure = []
    all_humidity = []

    for city, data in statistics.items():
        avg_temp = sum(data['temp']) / len(data['temp'])
        avg_feels_like = sum(data['feels_like']) / len(data['feels_like'])
        avg_temp_min = sum(data['temp_min']) / len(data['temp_min'])
        avg_temp_max = sum(data['temp_max']) / len(data['temp_max'])
        avg_pressure = sum(data['pressure']) / len(data['pressure'])
        avg_humidity = sum(data['humidity']) / len(data['humidity'])

        all_temp.append(avg_temp)
        all_feels_like.append(avg_feels_like)
        all_temp_min.append(avg_temp_min)
        all_temp_max.append(avg_temp_max)
        all_pressure.append(avg_pressure)
        all_humidity.append(avg_humidity)

        avg_statistics[city] = {
            'avg_temp': avg_temp,
            'avg_feels_like': avg_feels_like,
            'avg_temp_min': avg_temp_min,
            'avg_temp_max': avg_temp_max,
            'avg_pressure': avg_pressure,
            'avg_humidity': avg_humidity
        }

    avg_statistics['National Average'] = {
        'avg_temp': sum(all_temp)/len(all_temp),
        'avg_feels_like': sum(all_feels_like)/len(all_feels_like),
        'avg_temp_min': sum(all_temp_min)/len(all_temp_min),
        'avg_temp_max': sum(all_temp_max)/len(all_temp_max),
        'avg_pressure': sum(all_pressure)/len(all_pressure),
        'avg_humidity': sum(all_humidity)/len(all_humidity)
    }

    return avg_statistics


def compute_statistics(client, table_name, date):
    response = client.query(
        TableName=table_name,
        IndexName='DayIndex',
        ExpressionAttributeValues={
            ':v1': {
                'S': date
            }
        },
        ExpressionAttributeNames={"#day": "Day"},
        KeyConditionExpression='#day = :v1'
    )

    if response['Count'] == 0:
        # no data available, just return
        print('No data available')
        return

    all_data = response['Items']  # list of dictionaries
    all_statistics = []

    for d in all_data:
        statistics = Statistics(
            d['Name']['S'],
            d['Country']['S'],
            float(d['Temperature']['N']),
            float(d['Feels Like']['N']),
            float(d['Min Temperature']['N']),
            float(d['Max Temperature']['N']),
            float(d['Pressure']['N']),
            float(d['Humidity']['N'])
        )
        all_statistics.append(statistics)

    return compute_mean_statistics(all_statistics)


def create_and_save_file(avg_statistics, country, date):
    filename = f'{country}-{date}.json'
    with open('/tmp/' + filename, 'w') as f:
        json.dump(avg_statistics, f)

    s3_client = boto3.client('s3')
    bucket_name = f'bucket-sdcc-{country}'
    s3_client.create_bucket(Bucket=bucket_name)
    s3_client.upload_file('/tmp/' + filename, bucket_name, filename)



def lambda_handler(event, context):
    print(event)

    if event['Records'][0]['eventName'] == 'REMOVE':
        print('Unexpected event')
        return

    record_date = event['Records'][0]['dynamodb']['NewImage']['Day']['S']
    country = event['Records'][0]['dynamodb']['NewImage']['Country']['S']
    table_name = f'table-sdcc-{country}'

    dynamodb_client = boto3.client('dynamodb')

    # query all data with date = record_date
    is_date_present = query(dynamodb_client, record_date, table_name)

    if is_date_present:
        # the table already contains data with this date,
        # so the statistics for the previous day have already been computed
        return {
            'statusCode': 200,
            'body': json.dumps('No action performed.')
        }
    else:
        # this is the first tuple of the day, so we must compute statistics for the previous day
        # first, check if data from the previous day is present

        date = datetime.strptime(record_date, '%Y-%m-%d')
        prev_day = date - timedelta(days=1)
        prev_day = prev_day.isoformat()[:10]

        is_date_present = query(dynamodb_client, prev_day, table_name)
        if not is_date_present:
            print('No data found for yesterday')
            return {
                'statusCode': 200,
                'body': json.dumps('No action performed, as no data is present for yesterday.')
            }

        avg_statistics = compute_statistics(dynamodb_client, table_name, prev_day)
        create_and_save_file(avg_statistics, country, prev_day)

    return {
        'statusCode': 200,
        'body': json.dumps("Average statistics successfully computed and saved in the country's bucket.")
    }
