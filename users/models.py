from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from users.managers import CustomUserManager


class Profile(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=128, blank=True)
    email = models.EmailField(max_length=128, unique=True, db_index=True)
    phone = models.CharField(max_length=12, unique=True, db_index=True)
    descriptions = models.TextField(blank=True)
    expired = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=3))
    PROFILE_TYPE = (
        (1, 'АвтоБизнесмен'),
        (2, 'Автомобильная компания'),
        (3, 'Частное лицо'),
    )
    profile_type = models.IntegerField(choices=PROFILE_TYPE, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

    def get_phone_normal(self):
        normal_phone = '+38 ({}) {}-{}-{}'.format(self.phone[2:5], self.phone[5:8], self.phone[8:10], self.phone[10:])
        return normal_phone

    @property
    def is_payed(self):
        return bool(
            Order.objects.filter(user=self.id, date_start__lte=timezone.now(),
                                 date_expired__gte=timezone.now(), confirmed=True).first())


# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=13, unique=True)
#     descriptions = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)
#     expired = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=3))
#     PROFILE_TYPE = (
#         (1, 'АвтоБизнесмен'),
#         (2, 'Автомобильная компания'),
#         (3, 'Частное лицо'),
#     )
#     profile_type = models.IntegerField(choices=PROFILE_TYPE, null=True)

#     def __str__(self):
#         return self.user.email

#     @property
#     def is_payed(self):
#         return bool(
#             Order.objects.filter(user=self.user, date_start__lte=timezone.now(),
#                                  date_expired__gte=timezone.now(), confirmed=True).first())


#     class Meta:
#         verbose_name_plural = 'Profiles'


# @receiver(post_save, sender=User)
# def create_user_profile(instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(instance, **kwargs):
#     instance.profile.save()


class Plan(models.Model):
    name = models.CharField(max_length=128)
    price = models.CharField(max_length=128)
    period_days = models.IntegerField()
    money_count = models.IntegerField()

    def __str__(self):
        return f'Plan id={self.id}, plan={self.name}, price={self.price}'


class Order(models.Model):
    user = models.ForeignKey(Profile, null=True, on_delete=models.CASCADE)
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
        return f'Order id={self.id}, plan={self.plan.name}, user={self.user.name}'


class Telegram(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
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
