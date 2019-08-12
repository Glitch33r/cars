from django.db import models
from django.urls import reverse


class Mark(models.Model):
    name = models.CharField(max_length=128, blank=False)
    ria_id = models.IntegerField(null=True)
    eng = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Model(models.Model):
    name = models.CharField(max_length=128, blank=False)
    mark = models.ForeignKey(Mark, null=True, on_delete=models.CASCADE)
    ria_id = models.IntegerField(null=True)
    eng = models.CharField(max_length=128, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=128, blank=False)

    class Meta:
        ordering = ['name']

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
        return f'<SellerPhone: id={self.id} phone={self.phone}, deale={self.dealer}, is_blocked={self.is_blocked}>'

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
    seller = models.ForeignKey(SellerPhone, null=True, on_delete=models.SET_NULL)
    body = models.ForeignKey(Body, null=True, on_delete=models.SET_NULL)
    image = models.CharField(max_length=256, null=True)
    dtp = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    last_site_updatedAt = models.DateTimeField(blank=True, null=True)
    sold = models.BooleanField(default=False)
    cleared = models.BooleanField(default=True)
    olx_link = models.URLField(blank=True)
    ria_link = models.URLField(blank=True)
    ab_link = models.URLField(blank=True)
    bp_link = models.URLField(blank=True)
    ab_car_id = models.CharField(max_length=20, blank=True)
    rst_link = models.URLField(blank=True)
    price = models.IntegerField(null=True)

    class Meta:
        verbose_name_plural = 'Cars'
        ordering = ['-createdAt']

    def __str__(self):
        return '{} {}'.format(self.model.mark if self.model else '', self.model)

    @property
    def price_history(self):
        if self.pricehistory_set.all().count() > 1:
            return True
        return False


class PriceHistory(models.Model):
    SITE = (
        ('AR', 'AutoRia'),
        ('RST', 'RST'),
        ('OLX', 'OLX'),
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
