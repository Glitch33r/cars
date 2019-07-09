from __future__ import absolute_import, unicode_literals

from celery import shared_task
from .utils import CheckIsActiveUsers

from parsers.auto_ria.parser import AutoRiaUpdateParse, AutoRiaInnerParse
from parsers.ab.parser import Ab
from main.models import Car

@shared_task
def upd_ria(hours):
    AutoRiaUpdateParse(hours)
    return None


@shared_task
def check_is_active_users():
    CheckIsActiveUsers()
    return None

@shared_task
def inner_ria():
    AutoRiaInnerParse()
    return None


@shared_task
def xsum(numbers):
    return numbers

@shared_task
def upd_ab():
    ab_obj = Ab()
    for car in Car.objects.filter(ab_car_id__isnull=False, sold=False):
        ab_obj.update(car)
    return None
