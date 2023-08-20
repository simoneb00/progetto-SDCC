"""
this file retrieves weather conditions from the website openweathermap.org
the cities considered are specified in the file cities.csv.
"""
import csv
import subprocess

import requests
import os
from src.python.utils import random_subset_generator


class City:
    def __init__(self, name, country, lat, lon, data=None):
        self.name = name
        self.country = country
        self.lat = lat
        self.lon = lon
        self.data = data

    def set_data(self, data):
        self.data = data


def parse_csv_file(file_path):
    cities = []
    codes = []

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                city = row["City"]
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


def retrieve_cities(api_key):
    cities_array = []
    ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))
    cities, codes = parse_csv_file(ROOT_DIR + "/progetto-SDCC/data/cities.csv")
    countries = parse_csv_file_counties(ROOT_DIR + "/progetto-SDCC/data/countries.csv")

    subset = random_subset_generator.generate()

    subset_cities = []
    subset_codes = []

    print(subset)

    for i in subset:
        subset_cities.append(cities[i])
        subset_codes.append(codes[i])
        ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))

        try:
            subprocess.run(["bash", ROOT_DIR + "/progetto-SDCC/create_containers.sh", str.lower(codes[i][1:]),
                            str(8080 + countries.index(str.lower(codes[i][1:])))])
        except subprocess.CalledProcessError as e:
            print("Error in calling the containers' creation script")

    print(subset_cities)

    for i in range(0, len(subset_cities)):
        lat, lon = retrieve_coordinates(subset_cities[i], subset_codes[i], api_key)
        cities_array.append(City(subset_cities[i], subset_codes[i], lat, lon))
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
    ROOT_DIR = os.path.dirname(os.path.abspath(os.curdir))
    cities, codes = parse_csv_file(ROOT_DIR + "/progetto-SDCC/data/cities.csv")
    codes_unique = list(set(codes))
    return codes_unique


# This returns a tuple [city, country, lat, lon, data]
def retrieve():
    api_key = "9ef842fefcbe90d181f3982133dadd61"
    cities = retrieve_cities(api_key)

    for city in cities:
        data = retrieve_weather_data(city.lat, city.lon, api_key)
        city.set_data(data)

    print("Data retrieved")
    return cities
