from datetime import datetime

from django.db.models import QuerySet

from main.models import PriceHistory


def format_date(date: datetime):
    return datetime.strftime(date, '%m.%d.%y  %H:%M:%S')


def format_str_bool(data: dict, key: str):
    if data.get(key):
        data[key] = bool(data[key])
    return data


def filter_cars(data: dict):

    if data.get('cleared'):
        data['cleared'] = bool(data['cleared'])

    pass


def serialize_cars(cars: QuerySet):
    response = []
    bad_key = ['_state', 'model_id', 'gearbox_id', 'location_id', 'fuel_id', 'color_id', 'phone_id', 'body_id']
    for car in cars:
        part_car = vars(car)
        part_car['fuel_type'] = getattr(car.fuel, 'name', None)
        part_car['mark'] = getattr(car.model.mark, 'name', None)
        part_car['model'] = getattr(car.model, 'name', None)
        part_car['price'] = [{'price': price.price, 'date': format_date(price.date_set)} for price in
                             PriceHistory.objects.filter(car=car)]
        part_car['gearbox'] = getattr(car.gearbox, 'name', None)
        part_car['body'] = getattr(car.body, 'name', None)
        part_car['location'] = getattr(car.location, 'name', None)
        part_car['color'] = getattr(car.color, 'name', None)
        part_car['fuel_type'] = getattr(car.fuel, 'name', None)
        part_car['createdAt'] = format_date(car.createdAt)
        part_car['updatedAt'] = format_date(car.updatedAt)
        part_car['last_site_updatedAt'] = format_date(car.last_site_updatedAt)
        [part_car.pop(key, None) for key in bad_key]
        response.append(part_car)
    return response
