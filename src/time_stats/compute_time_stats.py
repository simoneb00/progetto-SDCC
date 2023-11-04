import csv
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np


def retrieve_countries():
    with open('data/countries.csv') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)

        countries = []
        for row in csvreader:
            countries.append(row[0])
    return countries


def create_graph(cold_start_data, no_cold_start_data):
    plt.figure(figsize=(10, 6))
    bar_width = 0.35
    x = np.arange(len(cold_start_data))

    plt.bar(x - bar_width / 2, no_cold_start_data[:len(cold_start_data)], bar_width, label='No Cold Start', color='red')

    plt.bar(x + bar_width / 2, cold_start_data, bar_width, label='Cold Start', color='blue')

    plt.title('Time differences between times with and without Cold Start')
    plt.xlabel('Points')
    plt.ylabel('Time (s)')

    plt.legend()

    plt.grid(True)
    plt.show()


def compute():
    countries = retrieve_countries()
    no_cold_start_data = []
    cold_start_data = []

    for country in countries:
        # Leggi il primo file CSV
        with open(f'time_data/volume_{country}/statistics.csv') as csvfile1:
            csvreader1 = csv.reader(csvfile1)
            next(csvreader1, None)  # Salta l'intestazione

            # Leggi il secondo file CSV
            with open(f'time_data/volume_data_generator/statistics_{country}.csv') as csvfile2:
                csvreader2 = csv.reader(csvfile2)
                next(csvreader2, None)  # Salta l'intestazione

                for row1, row2 in zip(csvreader1, csvreader2):
                    city1, time1, cold_start1 = row1
                    city2, time2 = row2

                    # Converte i tempi in oggetti datetime
                    time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S.%f')
                    time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S.%f')

                    # Calcola la differenza di tempo in secondi
                    time_diff = (time1 - time2).total_seconds()

                    if cold_start1 == 'False':
                        no_cold_start_data.append(time_diff)
                    else:
                        cold_start_data.append(time_diff)

    print(f'Based on {len(cold_start_data)} times with cold start and {len(no_cold_start_data)} '
          'times without cold start, we get the following results:')
    print(f'Avg time with cold start: {sum(cold_start_data) / len(cold_start_data)}')
    print(f'Avg time without cold start: {sum(no_cold_start_data) / len(no_cold_start_data)}')

    create_graph(cold_start_data, no_cold_start_data)


if __name__ == "__main__":
    compute()
