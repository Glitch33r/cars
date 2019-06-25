from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=False)
    expiredAt = models.DateTimeField(blank=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = 'Profiles'


class Plan(models.Model):
    name = models.CharField(max_length=128)
    price = models.CharField(max_length=128)
    period_days = models.IntegerField()
    money_count = models.IntegerField()

    def __str__(self):
        return f'Plan id={self.id}, plan={self.name}, price={self.price}'


class Order(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, null=True, on_delete=models.SET_NULL)
    date_transaction = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)
    confirmed = models.BooleanField(default=False)
    date_start = models.DateTimeField()
    date_expired = models.DateTimeField()

    @property
    def get_plan_days(self):
        return int(self.plan.period_days)

    def __str__(self):
        return f'Order id={self.id}, plan={self.plan.name}, user={self.user.first_name}'


class Mark(models.Model):
    name = models.CharField(max_length=128, blank=False)
    ria_id = models.IntegerField(null=True)
    eng = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=128, blank=False)
    mark = models.ForeignKey(Mark, null=True, on_delete=models.CASCADE)
    ria_id = models.IntegerField(null=True)
    eng = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=128, blank=False)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Gearbox(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Body(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Fuel(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class SellerPhone(models.Model):
    phone = models.CharField(max_length=1024, unique=True)



class Car(models.Model):
    model = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL)
    gearbox = models.ForeignKey(Gearbox, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    fuel = models.ForeignKey(Fuel, null=True, on_delete=models.SET_NULL)
    color = models.ForeignKey(Color, null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(null=True)
    mileage = models.IntegerField(null=True)
    engine = models.FloatField(null=True)
    description = models.TextField(null=True)
    phone = models.ForeignKey(SellerPhone, null=True, on_delete=models.SET_NULL)
    body = models.ForeignKey(Body, null=True, on_delete=models.SET_NULL)
    image = models.CharField(max_length=256)
    dtp = models.BooleanField(default=False)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField(blank=True)
    last_site_updatedAt = models.DateTimeField(blank=True)
    sold = models.BooleanField(default=False)
    cleared = models.BooleanField(default=True)
    olx_link = models.URLField(blank=True)
    ria_link = models.URLField(blank=True)
    ab_link = models.URLField(blank=True)
    rst_link = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'Cars'
        ordering = ['-createdAt']

    def __str__(self):
        if self.updatedAt:
            return '{} {} - last update {}'.format(self.model.mark.name, self.model.name, self.updatedAt.strftime("%H:%M %d.%m.%Y"))
        return '{} {}'.format(self.model.mark.name, self.model.name)


class PriceHistory(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    price = models.IntegerField()
    date_set = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'price_history'

    def __str__(self):
        return f'<PriceHistory: price={self.price}, date_set={self.date_set}>'


class Filter(models.Model):
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
    model = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL)
    mark = models.ForeignKey(Mark, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(Location, null=True, on_delete=models.SET_NULL)
    gearbox = models.CharField(choices=GEAR_BOX_TYPE, max_length=5, default=GEAR_BOX_TYPE[0][0])
    sell = models.CharField(choices=SELL_TYPE, max_length=8, default=SELL_TYPE[0][0])
    cleared = models.CharField(choices=CLEARED_TYPE, max_length=7, default=CLEARED_TYPE[0][0])
    accident = models.CharField(choices=ACCIDENT_TYPE, max_length=3, default=ACCIDENT_TYPE[0][0])

    class Meta:
        managed = False
