from datetime import datetime


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


