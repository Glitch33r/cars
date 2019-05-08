from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=False)
    expiredAt = models.DateTimeField(blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = 'Profiles'

    pass


class FilterForm(models.Model):
    GEAR_BOX_TYPE = (
        ('ANY', 'Любая КПП'),
        ('AUTO', 'Автоматическая'),
        ('MANUAL', 'Механическая'),
    )

    SELL_TYPE = (
        ('ACT', 'Актуальные(только в Продаже)'),
        ('SOLD', 'Проданные'),
        ('ACT_SOLD', 'Актуальные и проданные'),
    )

    CLEARED_TYPE = (
        ('CLR', 'Растаможенные'),
        ('NOT_CLR', 'Не растаможенные'),
        ('ANY', 'Любая реестрация'),
    )

    ACCIDENT_TYPE = (
        ('NO', 'без ДТП'),
        ('YES', 'после ДТП'),
        ('ANY', 'с ДТП и без'),
    )

    model = models.ForeignKey('Model', null=True, on_delete=models.SET_NULL)
    mark = models.ForeignKey('Mark', null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey('Location', null=True, on_delete=models.SET_NULL)

    class Meta:
        managed = False


class Model(models.Model):
    name = models.CharField(max_length=128, blank=False)

    def __str__(self):
        return self.name


class Mark(models.Model):
    name = models.CharField(max_length=128, blank=False)
    model = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Location(models.Model):
    region = models.CharField(max_length=128, blank=False)

    def __str__(self):
        return self.region


class Fuel(models.Model):
    name = models.CharField(max_length=128, blank=False)

    def __str__(self):
        return self.name


class Body(models.Model):
    name = models.CharField(max_length=128, blank=False)

    def __str__(self):
        return self.name
