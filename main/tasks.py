from __future__ import absolute_import, unicode_literals


from celery import shared_task

from parsers.utils import CheckUserFilters


@shared_task
def check_user_filters(car, update=False):
    CheckUserFilters(car, update=update)
    return None