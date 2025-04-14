import json
import time

import requests

from classes.shared.cache import Cache
from classes.vehicles.vehicle import Vehicle
from settings import API_USERNAME, API_PASSWORD


def check_api_tokens() -> dict:
    tokens = Cache.get_cached_api_tokens()
    current_timestamp = time.time()

    if not tokens['access'] or tokens['access_expires'] <= current_timestamp:
        if tokens['refresh'] and tokens['refresh_expires'] > current_timestamp:
            refresh_api_tokens(tokens)
        else:
            get_api_tokens()
    else:
        print('Cached token retrieved')

    return Cache.get_cached_api_tokens()

def get_api_tokens():
    response = requests.post('http://127.0.0.1:8000/api/token/',
                             data={'username': API_USERNAME, 'password': API_PASSWORD})

    if response.status_code == 200:
        Cache.set_api_tokens(response.json())
        print('Login successful')
    else:
        print(f'Login error {response.status_code}: {response.text}')

def refresh_api_tokens(tokens: dict):
    response = requests.post('http://127.0.0.1:8000/api/token/refresh/',
                             data={'refresh': tokens['refresh']})

    if response.status_code == 200:
        tokens['access'] = response.json()['access']
        tokens['access_expires'] = response.json()['access_expires']
        Cache.set_api_tokens(tokens)
        print('Login successful')
    else:
        print(f'Login error {response.status_code}: {response.text}')

def api_post_vehicle(vehicle: Vehicle):

    api_tokens = check_api_tokens()
    available_modification_as_json = json.dumps(vehicle.modifications)
    print(available_modification_as_json)

    response = requests.post('http://127.0.0.1:8000/api/admin/vehicle/',
                             data={
                                'name': vehicle.name,
                                'page_url': vehicle.page_url,
                                'image_url': vehicle.image_url,
                                'capacity': vehicle.capacity,
                                'speed_kmh': vehicle.speed_km,
                                'speed_mph': vehicle.speed_miles,
                                'price': vehicle.price,
                                'available': vehicle.available,
                                'available_modifications': available_modification_as_json,
                                'category': vehicle.category,
                                'type': vehicle.type,
                                'body_style': vehicle.body_style,
                                'drivetrain': vehicle.drivetrain,
                             },
                             headers={'authorization' : 'Bearer ' + api_tokens['access']})

    if response.status_code == 201:
        print("Vehicle post successful")
    else:
        print(f'Post error {response.status_code}: {response.text}')