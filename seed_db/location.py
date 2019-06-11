import json

import requests

from main.models import Location
from .auto_ria_api import AutoRiaAPI


def seed_table():
    for locate in json.loads(requests.get(f'https://developers.ria.com/auto/states?api_key={AutoRiaAPI.key}').content):
        Location(region=locate['name'].lower()).save()
