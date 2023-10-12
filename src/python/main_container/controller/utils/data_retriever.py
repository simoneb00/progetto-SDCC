"""
this file retrieves weather conditions from the website openweathermap.org
the cities considered are specified in the file cities.csv.
"""
import csv

import requests
import os

from . import random_subset_generator
from model import city


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

    cities, codes = parse_csv_file("app/data/cities.csv")
    countries = parse_csv_file_counties("app/data/countries.csv")


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
    cities, codes = parse_csv_file("app/data/cities.csv")
    codes_unique = list(set(codes))
    return codes_unique


def get_all_cities():
    cities, codes = parse_csv_file("app/data/cities.csv")
    return cities

# This returns a tuple [city, country, lat, lon, data]
def retrieve():
    api_key = "9ef842fefcbe90d181f3982133dadd61"
    cities = retrieve_cities_and_codes(api_key)

    for city in cities:
        data = retrieve_weather_data(city.lat, city.lon, api_key)
        city.set_data(data)

    return cities
