class Packet:
    def __init__(self, name, country, temp, feels_like, temp_min, temp_max, pressure, humidity, date_time):
        self.name = name
        self.country = country
        self.temp = temp
        self.feels_like = feels_like
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.pressure = pressure
        self.humidity = humidity
        self.date_time = date_time