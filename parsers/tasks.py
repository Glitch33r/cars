from __future__ import absolute_import, unicode_literals

from celery import shared_task

from main.utils import init_ab_utils
from .utils import CheckIsActiveUsers

from parsers.auto_ria.parser import AutoRiaUpdateParse, AutoRiaInnerParse



@shared_task
def inner_ria():
    AutoRiaInnerParse()
    return None


@shared_task
def upd_ria(hours):
    AutoRiaUpdateParse(hours)
    return None


@shared_task
def check_is_active_users():
    CheckIsActiveUsers()
    return None


@shared_task
def xsum(numbers):
    return numbers


@shared_task
def inner_ab():
    init_ab_utils()
    return None
