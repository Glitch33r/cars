from django.contrib import admin

from main.models import UserFilter, Order, Plan


@admin.register(UserFilter)
class UserFilter(admin.ModelAdmin):
    list_display = ['user', 'blocked']

@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ['user', 'plan']

@admin.register(Plan)
class Plan(admin.ModelAdmin):
    list_display = ['name', 'period_days']
