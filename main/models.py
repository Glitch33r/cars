from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


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

    def __str__(self):
        return self.phone

    def count(self):
        """Returns the number of seller’s cars"""
        return self.car_set.count()

    def status(self):
        """Returns seller status"""
        if self.count() < 20:
            return 'Продавец'
        return 'Перекупщик'

    def get_absolute_url(self):
        return reverse('seller', kwargs={'pk': self.pk})


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
    image = models.CharField(max_length=256, null=True)
    dtp = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now=True)
    updatedAt = models.DateTimeField(blank=True, null=True)
    last_site_updatedAt = models.DateTimeField(blank=True, null=True)
    sold = models.BooleanField(default=False)
    cleared = models.BooleanField(default=True)
    olx_link = models.URLField(blank=True)
    ria_link = models.URLField(blank=True)
    ab_link = models.URLField(blank=True)
    ab_car_id = models.CharField(max_length=20, blank=True)
    rst_link = models.URLField(blank=True)
    price = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = 'Cars'
        ordering = ['-last_site_updatedAt']

    def __str__(self):
        return '{} {}'.format(self.model.mark.name, self.model.name)


class PriceHistory(models.Model):
    SITE = (
        ('AR', 'AutoRia'),
        ('RST', 'RST'),
        ('AB', 'Auto Bazar'),
        ('BP', 'Besplatka'),
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    price = models.IntegerField()
    date_set = models.DateTimeField(auto_now=True)
    site = models.CharField(choices=SITE, max_length=3)

    class Meta:
        verbose_name_plural = 'price_history'

    def __str__(self):
        return f'<PriceHistory: price={self.price}, date_set={self.date_set}>'

    def save(self, *args, **kwargs):
        # if self.site == 'AR':
        self.car.price = self.price
        self.car.save()
        super().save(*args, **kwargs)
