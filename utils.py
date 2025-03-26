import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

API_KEY = '371e1360-5397-45a5-9639-2e7da34bd060'


def get_static_api_image(ll, z, size):
    server = 'https://static-maps.yandex.ru/v1?'
    map_params = {
        'll': ','.join(map(str, ll)),
        'apikey': API_KEY,
        'z': z,
        'size:': ','.join(map(str, size))
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
