import csv
import os
import requests
from django.conf import settings
from decouple import config 


def load_fuel_prices():
    """
    Load fuel prices from a CSV file located in the project directory.
    """
    fuel_prices = []
    fuel_prices_file_path = os.path.join(settings.BASE_DIR, 'fuel-prices-for-be-assessment.csv')

    try:
        with open(fuel_prices_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                fuel_prices.append({
                    'truckshop_name': row['Truckstop Name'],
                    'address': row['Address'],
                    'price': float(row['Retail Price']),
                    'city': row['City'],
                })
    except FileNotFoundError:
        print(f"File not found at: {fuel_prices_file_path}")
    except Exception as e:
        print(f"An error occurred while loading the fuel prices: {e}")

    return fuel_prices


def select_fuel_stops(route_data, start_city, end_city):
    """
    Select fuel stops near the given start and end cities, 
    sorted by price, and calculate the total fuel cost.
    """
    fuel_prices = load_fuel_prices()

    relevant_stations = [
        station for station in fuel_prices
        if station['city'].lower() in {start_city.lower(), end_city.lower()}
    ]

    fuel_stops = sorted(relevant_stations, key=lambda x: x['price'])
    total_fuel_cost = sum(station['price'] for station in fuel_stops)

    return fuel_stops, total_fuel_cost


def get_coordinates(city_name):
    """
    Get latitude and longitude for a given city using a geocoding API.
    """
    api_key = config("OPENCAGE_API_KEY")
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={api_key}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['results']:
                coordinates = data['results'][0]['geometry']
                return f"{coordinates['lat']},{coordinates['lng']}"
    except Exception as e:
        print(f"Error fetching coordinates for {city_name}: {e}")

    return None, None
