"""
this file retrieves weather conditions from the website openweathermap.org
the cities considered are specified in the file cities.csv.
"""
import csv
import datetime
import os
import socket
import time

import requests
import json

import random_subset_generator
import city


def parse_csv_file(file_path):
    cities = []
    codes = []

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                city = row['City']
                code = row[" ISO_3166_code"]
                cities.append(city)
                codes.append(code)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except csv.Error as e:
        print(f"Error while reading CSV: {e}")
        return None

    return cities, codes


def parse_csv_file_counties(file_path):
    countries = []

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                countries.append(row["Code"])
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except csv.Error as e:
        print(f"Error while reading CSV: {e}")
        return None

    return countries


def retrieve_coordinates(city, country, api_key):
    url = f"https://api.openweathermap.org/geo/1.0/direct?q={city},{country}&appid={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if data and len(data) > 0:
            lat = data[0]["lat"]
            lon = data[0]["lon"]

        return lat, lon

    except requests.exceptions.RequestException as e:
        print("Error during API request:", e)
        return None


def retrieve_cities_and_codes(api_key):
    cities_array = []

    cities, codes = parse_csv_file("cities.csv")
    countries = parse_csv_file_counties("countries.csv")

    subset = random_subset_generator.generate()  # Number from 1 to 55

    subset_cities = []
    subset_codes = []

    for i in subset:
        subset_cities.append(cities[i - 1])
        subset_codes.append(codes[i - 1])

    for i in range(0, len(subset_cities)):
        country_number = countries.index(str.lower(subset_codes[i][1:]))
        lat, lon = retrieve_coordinates(subset_cities[i], subset_codes[i], api_key)
        cities_array.append(city.City(subset_cities[i], subset_codes[i], lat, lon, country_number))
    return cities_array


def retrieve_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Error during API request:", e)
        return None


def retrieve_countries():
    cities, codes = parse_csv_file("cities.csv")
    codes_unique = list(set(codes))
    return codes_unique


def get_all_cities():
    cities, codes = parse_csv_file("cities.csv")
    return cities


def send_data_to_dest_container(city, config):
    dest_country = city.country.lower()[1:]
    container_name = f'container_{dest_country}'

    print(f'[INFO] Sending data to {container_name}')

    params = {'country': dest_country}
    response = requests.get(config.get('service_registry_endpoint'), params=params)
    if response.status_code != 200:
        raise Exception('An error occurred in calling the service registry.')

    return_data = json.loads(response.text)
    port_number = return_data.get('port_number')

    endpoint = f'http://{container_name}:{port_number}/{dest_country}'

    try:
        with open("data.json", 'w') as file:
            json.dump(city.data, file)

        with open("data.json", 'r') as file:
            files = {'file': file}
            headers = {"X-Source-Container": 'data_generator_container'}

            response = requests.post(endpoint, files=files, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                print('Request correctly received and processed')

        if response.status_code != 200:
            print(f'Something went wrong - response status code {response.status_code}')

    except requests.ConnectionError:
        # In this case, the destination container is not active, so data must be sent to the main container
        return False

    print(f'[INFO] Data successfully sent to {container_name}')
    return True


# This returns a tuple [city, country, lat, lon, data]
def retrieve():
    with open('config.json', 'r') as file:
        config = json.load(file)

    api_key = config.get('api_key')
    round_index = 1

    while True:

        print(f"\n***************************************** ROUND {round_index} *****************************************")

        # the following list is needed to keep track of the those containers contacted by this container
        # (so not from the main container), in order to make the round handling in the main container possible.
        active_countries = []

        cities = retrieve_cities_and_codes(api_key)

        for city in cities:
            data = retrieve_weather_data(city.lat, city.lon, api_key)
            city.set_data(data)

            now = datetime.datetime.now()
            print(f'[INFO] Data generated at time {now}')

            # Save generation time into a csv file
            filename = f'/volume/statistics_{city.country.lower()[1:]}.csv'
            file_exists = os.path.isfile(filename)

            with open(filename, 'a') as f:
                csv_writer = csv.writer(f)
                if not file_exists:
                    csv_writer.writerow(['city', 'time'])
                csv_writer.writerow([city.name, now])

            # Pack and send data
            send_data = {
                'name': city.name,
                'country': city.country,
                'lat': city.lat,
                'lon': city.lon,
                'country_number': city.country_number,
                'data': city.data
            }

            data_sent = send_data_to_dest_container(city, config)

            if data_sent:
                active_countries.append(city.country.lower()[1:])

            if not data_sent:
                print('[INFO] Cannot connect to the destination container, redirecting the request to main container')
                endpoint = config.get('main_container_endpoint_send')
                response = requests.post(url=endpoint, json=send_data)
                if response.status_code == 200:
                    print('[INFO] Request successfully sent to main container')
                else:
                    print(f'Something went wrong - response status code {response.status_code}')

            print('\n')

        # end of round, send message and sleep for 60 seconds
        # we need to send to main container both the round_index and the list of active countries
        endpoint = config.get('main_container_endpoint_end_round')
        round_index = round_index + 1

        data = {
            'round_index': round_index,
            'list': active_countries
        }

        requests.post(url=endpoint, json=data)

        print('[INFO] End of round, sent message\n')

            print(f'Sent data relative to city {city.name}')

        print('End of round: sleeping for 60 seconds')
        time.sleep(60)



if __name__ == '__main__':
    retrieve()
