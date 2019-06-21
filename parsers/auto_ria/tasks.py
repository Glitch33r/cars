from __future__ import absolute_import, unicode_literals

import time

from celery import shared_task

from parsers.auto_ria.parser import AutoRiaUpdateParse, AutoRiaInnerParse


@shared_task
def upd_ria():
    AutoRiaUpdateParse()
    return None


@shared_task
def inner_ria():
    AutoRiaInnerParse()
    return None


@shared_task
def mul(x, y):
    time.sleep(5)
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)
