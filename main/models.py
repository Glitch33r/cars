from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=False)
    expiredAt = models.DateTimeField(blank=True)

    pass


class Filter(models.Model):
    GEAR_BOX_TYPE = (
        ('ANY', ''),
        ('AUTO', ''),
        ('MANUAL', ''),
    )

    SELL_TYPE = (
        ('ACT', ''),
        ('SOLD', ''),
        ('ACT_SOLD', ''),
    )

    CLEARED_TYPE = (
        ('CLR', ''),
        ('NOT_CLR', ''),
        ('ANY', ''),
    )

    ACCIDENT_TYPE = (
        ('NO', ''),
        ('YES', ''),
        ('ANY', ''),
    )
    pass


# class Model:
#     pass
#
# class Mark:
#     pass
#
#
# class Location:
#     pass
#

