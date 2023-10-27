"""
this file retrieves weather conditions from the website openweathermap.org
the cities considered are specified in the file cities.csv.
"""
import csv
import datetime
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


def send_data_to_dest_container(city):
    dest_country = city.country.lower()[1:]
    container_name = f'container_{dest_country}'

    print(f'Trying to send data to {container_name}')

    # try to contact destination container
    params = {'country': dest_country}
    response = requests.get('http://service_registry_container:9000/service-registry', params=params)
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
            headers = requests.utils.default_headers()

            response = requests.post(endpoint, files=files, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                print('Request correctly received and processed')

        if response.status_code != 200:
            print(f'Something went wrong - response status code {response.status_code}')

    except requests.ConnectionError:
        return False

    print(f'Data successfully sent to {container_name}')
    return True



# This returns a tuple [city, country, lat, lon, data]
def retrieve():
    api_key = "9ef842fefcbe90d181f3982133dadd61"
    round_index = 1
    active_countries = []

    while True:

        print(f"\n****************************************** ROUND {round_index} ******************************************")
        print(f"Cannot connect to the destination container, redirecting the request to the main container")

        # this list is needed to keep track of the countries' containers directly contacted by this container,
        # in order to make the round handling in the main container possible.
        active_countries = []

        cities = retrieve_cities_and_codes(api_key)

        for city in cities:
            data = retrieve_weather_data(city.lat, city.lon, api_key)
            city.set_data(data)

            now = datetime.datetime.now()
            print(f'Data generated at time {now}')

            send_data = {
                'name': city.name,
                'country': city.country,
                'lat': city.lat,
                'lon': city.lon,
                'country_number': city.country_number,
                'data': city.data
            }

            print(f'Sending data for city {city.name}')
            dataSent = send_data_to_dest_container(city)

            if dataSent:
                active_countries.append(city.country.lower()[1:])

            if not dataSent:
                print('Cannot connect to the destination container, redirecting the request to the main container')
                # in this case, the destination container is not active, so redirect the request on the main container
                endpoint = 'http://main_container:9001/send-data'
                response = requests.post(url=endpoint, json=send_data)
                if response.status_code != 200:
                    print(f'Something went wrong - response status code {response.status_code}')

            print('\n')

        # end of round, send message and sleep for 60 seconds
        # we need to send both the round_index and the list of active countries

        endpoint = 'http://main_container:9001/end-round/'
        round_index = round_index + 1

        data = {
            'round_index': round_index,
            'list': active_countries
        }

        requests.post(url=endpoint, json=data)

        print('End of round, sent message\n')

        time.sleep(60)



if __name__ == '__main__':
    retrieve()
