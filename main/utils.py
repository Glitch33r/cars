from datetime import datetime

from django.utils import timezone
import telebot
from .models import Telegram
from main.models import PriceHistory


def serialize_cars(cars):
    response = []
    bad_key = ['_state', 'model_id', 'gearbox_id', 'location_id', 'fuel_id', 'color_id', 'phone_id', 'body_id']
    for car in cars:
        part_car = vars(car)
        part_car['fuel_type'] = getattr(car.fuel, 'name', None)
        part_car['gearbox'] = getattr(car.gearbox, 'name', None)
        part_car['body'] = getattr(car.body, 'name', None)
        part_car['location'] = getattr(car.location, 'name', None)
        part_car['color'] = getattr(car.color, 'name', None)
        part_car['fuel_type'] = getattr(car.fuel, 'name', None)
        part_car['createdAt'] = datetime.strftime(car.createdAt, '%m.%d.%y  %H:%M:%S')
        part_car['updatedAt'] = datetime.strftime(car.updatedAt, '%m.%d.%y  %H:%M:%S')
        part_car['last_site_updatedAt'] = datetime.strftime(car.last_site_updatedAt, '%m.%d.%y %H:%M:%S')
        [part_car.pop(key, None) for key in bad_key]
        response.append(part_car)
    return response


# def celery_serialize_car(car):
#     bad_keys = ['_state', 'image', 'createdAt', 'updatedAt', 'last_site_updatedAt', 'sold', 'description', 'olx_link',
#                 'ab_link', 'ab_car_id', 'rst_link', 'mileage', 'engine', 'ria_link']
#     car_dict = vars(car)
#     car_dict['dealer'] = True if car.phone.count() >= 10 else False
#     car_dict['mark_id'] = car.model.mark.id
#     car_dict['price'] = PriceHistory.objects.filter(car=car, site='AR').order_by('-date_set').first().price
#     [car_dict.pop(key) for key in bad_keys]
#     print(car_dict)


def get_chat(profile):
    telegram = Telegram.objects.filter(user=profile.user).first()
    if telegram:
        return int(telegram.chat_id)
    return False


def tg_send_message(profile, car, update=False):
    bot = telebot.TeleBot('769710155:AAEzNRKxFG8-Jl5fETdf2WS9Wt2c1hkhzMw')
    message = ['появилась новая машина {} {} с ценой {}', '{} {} обновилась с ценой {}']
    chat = get_chat(profile)
    if chat:
        message_send = message[bool(update)].format(car.model.mark.name, car.model.name, car.price)
        bot.send_message(chat, message_send)
