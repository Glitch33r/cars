import json

import requests

from parsers.choises import BODY, GEARBOX, FUEL, COLOR, LOCATION

from main.models import Location, Color, Gearbox, Fuel, Body, Mark, Model
from .auto_ria_api import AutoRiaAPI
from .models_merk_tuple import marks, models

way = '{}{}'


def seed(api_way, class_obj):
    for var in json.loads(requests.get(way.format(api_way, AutoRiaAPI.key)).content):
        var['name'] = var['name'].lower().replace(' ', '')
        class_obj(name=var['name'].lower()).save()


def seed_location():
    # seed('https://developers.ria.com/auto/states?api_key=', Location)
    python_locations = []
    for key,value in LOCATION.items():
        python_locations.append(Location(id=value, name=key))
    Location.objects.bulk_create(python_locations)

def seed_color():
    # seed('https://developers.ria.com/auto/colors?api_key=', Color)
    python_colors = []
    for key,value in COLOR.items():
        python_colors.append(Color(id=value, name=key))
    Color.objects.bulk_create(python_colors)


def seed_gearbox():
    # seed('https://developers.ria.com/auto/categories/2/gearboxes?api_key=', Gearbox)
    # Gearbox(name='робот').save()
    python_gearboxes = []
    for key, value in GEARBOX.items():
        python_gearboxes.append(Gearbox(id=value, name=key))
    Gearbox.objects.bulk_create(python_gearboxes)


def seed_fuel():
    # seed('https://developers.ria.com/auto/type?api_key=', Fuel)
    python_fuels = []
    for key, value in FUEL.items():
        python_fuels.append(Fuel(id=value, name=key))
    Fuel.objects.bulk_create(python_fuels)


def seed_body():
    # for var in json.loads(requests.get(
    #         way.format('https://developers.ria.com/auto/categories/1/bodystyles?api_key=', AutoRiaAPI.key)).content):
    #     var['name'] = var['name'].lower().replace(' ', '')
    #     Body(name=var['name'].lower()).save()
    python_bodies = []
    for key, value in BODY.items():
        python_bodies.append(Body(id=value, name=key))
    Body.objects.bulk_create(python_bodies)


def seed_mark():
    python_marks = []
    for mark in marks:
        python_marks.append(Mark(name=mark[1], ria_id=mark[2], eng=mark[3]))
    Mark.objects.bulk_create(python_marks)


def seed_model():
    python_models = []
    for model in models:
        python_models.append(Model(mark_id=model[1], name=model[2], ria_id=model[3], eng=model[4]))
    Model.objects.bulk_create(python_models)
