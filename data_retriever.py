"""
this file retrieves weather conditions from the website openweathermap.org
the cities considered are specified in the file cities.csv.
"""
import csv
import requests


class City:
    def __init__(self, name, code, lat, lon, data=None):
        self.name = name
        self.code = code
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
    cities, codes = parse_csv_file("cities.csv")
    for i in range(0, len(cities)):
        lat, lon = retrieve_coordinates(cities[i], codes[i], api_key)
        cities_array.append(City(cities[i], codes[i], lat, lon))
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


def entry_point():
    api_key = "9ef842fefcbe90d181f3982133dadd61"
    cities = retrieve_cities(api_key)

    for city in cities:
        data = retrieve_weather_data(city.lat, city.lon, api_key)
        city.set_data(data)

    print("Data retrieved")
    return cities
