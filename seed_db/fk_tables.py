import json

import requests

from main.models import Location, Color, Gearbox, Fuel, Body, Mark, Model
from .auto_ria_api import AutoRiaAPI

way = '{}{}'


def seed(api_way, class_obj):
    for var in json.loads(requests.get(way.format(api_way, AutoRiaAPI.key)).content):
        var['name'] = var['name'].lower().replace(' ', '')
        class_obj(name=var['name'].lower()).save()


def seed_location():
    seed('https://developers.ria.com/auto/states?api_key=', Location)


def seed_color():
    seed('https://developers.ria.com/auto/colors?api_key=', Color)


def seed_gearbox():
    seed('https://developers.ria.com/auto/categories/2/gearboxes?api_key=', Gearbox)


def seed_fuel():
    seed('https://developers.ria.com/auto/type?api_key=', Fuel)


def seed_body():
    for var in json.loads(requests.get(
            way.format('https://developers.ria.com/auto/categories/1/bodystyles?api_key=', AutoRiaAPI.key)).content):
        var['name'] = var['name'].lower().replace(' ', '')
        Body(id=var['value'], name=var['name'].lower()).save()
    seed('https://developers.ria.com/auto/categories/1/bodystyles?api_key=', Body)


def seed_mark():
    from .models_merk_tuple import marks
    python_marks = []
    for mark in marks:
        python_marks.append(Mark(id=mark[0], name=mark[1], ria_id=mark[2], eng=mark[3]))
    Mark.objects.bulk_create(python_marks)


def seed_model():
    from .models_merk_tuple import models
    python_models = []
    for model in models:
        python_models.append(Model(id=model[0], mark_id=model[1], name=model[2], ria_id=model[3], eng=model[4]))
    Model.objects.bulk_create(python_models)


if __name__ == '__main__':
    pass
    # seed_location()
    # seed_color()
    # seed_fuel()
    # seed_color()
    # seed_gearbox()
    seed_body()
