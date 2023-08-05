"""
Only used for testing
"""

import container
import data_retriever


if __name__ == "__main__":
    cities = data_retriever.entry_point()
    packets = container.pack_data(cities)

    for packet in packets:
        print(f"[{packet.name}, {packet.country}, {packet.temp}, {packet.feels_like},{packet.temp_min}, {packet.temp_max}, {packet.humidity}, {packet.pressure}, {packet.date_time}]")