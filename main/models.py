from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=False)
    descriptions = models.TextField(null=True)
    is_active = models.BooleanField(default=False)
    expiredAt = models.DateTimeField(blank=True)

    def __str__(self):
        return self.user.email

    @property
    def is_payed(self):
        return bool(
            Order.objects.filter(user=self.user, date_start__lte=timezone.now(), date_expired__gte=timezone.now(),
                                 confirmed=True).first())

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
        return f'Order id={self.id}, plan={self.plan.name}, user={self.user.username}'


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
    dealer = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.phone

    @property
    def car_count(self):
        """Returns the number of seller’s cars"""
        return self.car_set.count()

    @property
    def status(self):
        """Returns seller status"""
        if self.car_count > 9 or self.dealer:
            return 'Диллер'
        return 'Продавец'

    @property
    def is_dealer(self):
        if self.car_count >= 10:
            return True
        return False

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
        ordering = ['-createdAt']

    def __str__(self):
        return '{} {}'.format(self.model.mark if self.model.mark is not None else '', self.model)

    @property
    def price_history(self):
        if self.pricehistory_set.all().count() > 1:
            return True
        return False


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
        if self.site == 'AR' or not bool(PriceHistory.objects.filter(car=self.car, site='AR').count()):
            self.car.price = self.price
            self.car.save()
        super().save(*args, **kwargs)


class Telegram(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=24)
    last_send_time = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = 'telegram'

    def __str__(self):
        return f'<Telegram: user={self.user.username}, last_send_time={self.last_send_time}>'


class UserFilter(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    model_id = models.IntegerField(null=True)
    mark_id = models.IntegerField(null=True)
    gearbox_id = models.IntegerField(null=True)
    location_id = models.IntegerField(null=True)
    fuel_id = models.IntegerField(null=True)
    # color_id = models.IntegerField()
    year_start = models.IntegerField(null=True)
    year_finish = models.IntegerField(null=True)
    # mileage = models.IntegerField()
    # engine_id = models.IntegerField()
    body_id = models.IntegerField(null=True)
    dtp = models.BooleanField(default=False)
    cleared = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    dealer = models.BooleanField(default=False)
    # query_filter = models.CharField(max_length=256)
    car_ids = models.TextField(null=True)

    class Meta:
        verbose_name_plural = 'user_filter'

    def is_active(self):
        return self.user.is_payed

    @staticmethod
    def get_active():
        return UserFilter.objects.filter(user__is_active=True)

    def __str__(self):
        return f'<UserFilter: user={self.user.user.username}, dealer={self.dealer}>'
