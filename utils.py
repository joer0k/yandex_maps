import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

API_KEY_ST = '371e1360-5397-45a5-9639-2e7da34bd060'
API_KEY_GEO = 'd2f5711d-9e67-414c-aa2c-d7c0465aea3e'


def get_static_api_image(ll, z, size, theme, points):
    server = 'https://static-maps.yandex.ru/v1?'
    map_params = {
        'll': ','.join(map(str, ll)),
        'apikey': API_KEY_ST,
        'z': z,
        'size:': ','.join(map(str, size)),
        'theme': theme,
        'pt': '~'.join(points)
    }

    session = requests.Session()
    retry = Retry(total=10, connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    response = session.get(server, params=map_params)
    if response:
        return response.content
    else:
        return None


def get_ll(address):
    server = 'http://geocode-maps.yandex.ru/1.x/?'
    map_params = {
        'apikey': API_KEY_GEO,
        'geocode': address,
        'format': 'json',
    }
    session = requests.Session()
    retry = Retry(total=10, connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    response = session.get(server, params=map_params)
    if response:
        return response.json()["response"]["GeoObjectCollection"]["featureMember"][0]['GeoObject']
    else:
        return None
