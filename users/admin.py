from django.contrib import admin

from users.models import UserFilter, Order, Plan, Profile


@admin.register(UserFilter)
class UserFilter(admin.ModelAdmin):
    list_display = ['user', 'blocked']

@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ['user', 'plan']

@admin.register(Plan)
class Plan(admin.ModelAdmin):
    list_display = ['name', 'period_days']


admin.site.register(Profile)
