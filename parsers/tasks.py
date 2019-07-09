from __future__ import absolute_import, unicode_literals

from celery import shared_task
from .utils import CheckIsActiveUsers

from parsers.auto_ria.parser import AutoRiaUpdateParse, AutoRiaInnerParse


@shared_task
def upd_ria():
    AutoRiaUpdateParse(2)
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
