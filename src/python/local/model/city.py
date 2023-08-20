class City:
    def __init__(self, name, country, lat, lon,country_number, data=None):
        self.name = name
        self.country = country
        self.lat = lat
        self.lon = lon
        self.country_number = country_number
        self.data = data

    def set_data(self, data):
        self.data = data