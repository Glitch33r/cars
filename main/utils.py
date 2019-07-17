from datetime import datetime
from threading import Thread

from parsers.ab.parser import Ab



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





def init_ab_utils():
    ab_obj = Ab()
    thread_1 = Thread(target=ab_obj.parse, args=(1, 100))
    thread_2 = Thread(target=ab_obj.parse, args=(101, 200))
    thread_3 = Thread(target=ab_obj.parse, args=(201, 300))
    # thread_4 = Thread(target=ab_obj.parse, args=(301, 400))
    # thread_5 = Thread(target=ab_obj.parse, args=(401, 500))
    thread_1.start()
    thread_2.start()
    thread_3.start()
    # thread_4.start()
    # thread_5.start()
    thread_1.join()
    thread_2.join()
    thread_3.join()
