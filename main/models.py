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


class Car(models.Model):
    GEAR_BOX_TYPE = (
        ('AUTO', 'Автоматическая'),
        ('MANUAL', 'Механическая'),
    )

    FUEL_TYPE = (
        ('PETROL', 'Бензин'),
        ('DIESEL', 'Дизель'),
        ('OTHER', 'Другой'),
    )

    BODY = (
        ('SEDAN', 'Седан'),
        ('SUV', 'Внедорожник'),
        ('MINIVAN', 'Минивэн'),
        ('HATCHBACK', 'Хэтчбек'),
        ('UNIVERSAL', 'Универсал'),
        ('COUPE', 'Купе'),
        ('CONVERTIBLE', 'Кабриолет'),
        ('PICKUP', 'Пикап'),
        ('OTHER', 'Другой'),
    )

    model = models.ForeignKey('Model', null=True, on_delete=models.SET_NULL)
    mark = models.ForeignKey('Mark', null=True, on_delete=models.SET_NULL)
    gearbox = models.CharField(choices=GEAR_BOX_TYPE, max_length=5)
    location = models.ForeignKey('Location', null=True, on_delete=models.SET_NULL)
    fuel = models.CharField(choices=GEAR_BOX_TYPE, max_length=5)
    color = models.CharField(max_length=64)
    year = models.CharField(max_length=64)
    mileage = models.CharField(max_length=64)
    engine = models.CharField(max_length=64)
    description = models.CharField(max_length=1024)
    price = models.CharField(max_length=64)
    phones = models.CharField(max_length=255)
    body = models.CharField(choices=GEAR_BOX_TYPE, max_length=12)

    class Meta:
        verbose_name_plural = 'Cars'


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
    model = models.ForeignKey('Model', null=True, on_delete=models.SET_NULL)
    mark = models.ForeignKey('Mark', null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey('Location', null=True, on_delete=models.SET_NULL)
    gearbox = models.CharField(choices=GEAR_BOX_TYPE, max_length=5, default=GEAR_BOX_TYPE[0][0])
    sell = models.CharField(choices=SELL_TYPE, max_length=8, default=SELL_TYPE[0][0])
    cleared = models.CharField(choices=CLEARED_TYPE, max_length=7, default=CLEARED_TYPE[0][0])
    accident = models.CharField(choices=ACCIDENT_TYPE, max_length=3, default=ACCIDENT_TYPE[0][0])

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
