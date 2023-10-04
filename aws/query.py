import json
import boto3

def dict_list_to_float_list(dict_list):
    float_list = []
    for dict in dict_list:
        float_list.append(float(dict['N']))
    return float_list


# this function retrieves all data relative to the request's city
def get_data(dynamodb_client, city, country):
    response = dynamodb_client.query(
        TableName='table-sdcc-' + country,
        ExpressionAttributeNames={"#name": "Name"},
        ExpressionAttributeValues={
            ':v1': {
                'S': city
            }
        },
        KeyConditionExpression='#name = :v1'
    )

    if response['Count'] == 0:
        return None

    all_data = response['Items']  # list of dictionaries

    all_temps = []
    all_feels_like = []
    all_min_temps = []
    all_max_temps = []
    all_pressures = []
    all_humidities = []

    for d in all_data:
        all_temps.append(d['Temperature'])
        all_feels_like.append(d['Feels Like'])
        all_min_temps.append(d['Min Temperature'])
        all_max_temps.append(d['Max Temperature'])
        all_pressures.append(d['Pressure'])
        all_humidities.append(d['Humidity'])

    all_temps = dict_list_to_float_list(all_temps)
    all_feels_like = dict_list_to_float_list(all_feels_like)
    all_min_temps = dict_list_to_float_list(all_min_temps)
    all_max_temps = dict_list_to_float_list(all_max_temps)
    all_pressures = dict_list_to_float_list(all_pressures)
    all_humidities = dict_list_to_float_list(all_humidities)

    return {
        'Avg Temperature': sum(all_temps) / len(all_temps),
        'Avg Feels Like': sum(all_feels_like) / len(all_feels_like),
        'Avg Min Temperature': sum(all_min_temps) / len(all_min_temps),
        'Avg Max Temperature': sum(all_max_temps) / len(all_max_temps),
        'Avg Pressure': sum(all_pressures) / len(all_pressures),
        'Avg Humidity': sum(all_humidities) / len(all_humidities)
    }


def lambda_handler(event, context):
    dynamodb_client = boto3.client('dynamodb')
    data = json.loads(event['body'])
    return_data = get_data(dynamodb_client, data.get('city'), data.get('country'))

    if return_data == None:
        return {
            'statusCode': 404,
            'body': 'There is no data available for this city.'
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(return_data)
        }

