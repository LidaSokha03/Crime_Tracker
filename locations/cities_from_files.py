from pathlib import Path
import csv


def region_to_cities(region):
    BASE_DIR = Path(__file__).parent
    filename = BASE_DIR / f'{region}.csv'
    with open(filename, 'r', encoding='utf-8') as file_name:
        return sorted([f'{t} {n}' for t, n in csv.reader(file_name, delimiter=',')], key=lambda x: x.split()[1])

def search_cities(region, beginning):
    cities = region_to_cities(region)
    return [city for city in cities if city.lower().split()[1].startswith(beginning.lower())]

# a = 'untitled folder/Crime_Tracker/locations/cities_from_files.py'

# # Поточна папка, де знаходиться скрипт
# BASE_DIR = Path(__file__).parent

# # Шлях до CSV-файлу
# filename = BASE_DIR / 'Вінницька.csv'

# with open(filename, encoding='utf-8') as f:
#     data = f.read()
#     print(data)