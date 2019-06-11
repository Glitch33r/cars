import json

from main.models import Mark, Model
from .auto_ria_api import AutoRiaAPI
import requests


def seed_table():
    way_mark = f'https://developers.ria.com/auto/categories/1/marks?api_key={AutoRiaAPI.key}'
    way_model = 'https://developers.ria.com/auto/categories/2/marks/{}/models?api_key=' + AutoRiaAPI.key
    marks = json.loads(requests.get(way_mark).content)
    for mark in marks:
        mark = Mark(name=mark['name'], ria_id=str(mark['value']))
        mark.save()
        model_list = []
        for model in json.loads(requests.get(way_model.format(mark.ria_id)).content):
            model = Model(name=model['name'], ria_id=str(model['value']), mark=mark)
            model_list.append(model)
        Model.objects.bulk_create(model_list)



if __name__ == '__main__':
    seed_table()

