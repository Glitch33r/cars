from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from users.models import UserFilter, Order, Plan, Profile
from users.forms import ProfileCreationForm, ProfileChangeForm


@admin.register(Profile)
class ProfileAdmin(UserAdmin):
    list_display = ('phone', 'email', 'is_active', 'is_superuser')
    search_fields = ('phone', 'email')
    fieldsets = (
        (None, {'fields': ('name', 'email', 'phone', 'password')}),
        ('Rules', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('date_joined', 'last_login')}),
    )
    form = ProfileChangeForm
    add_form = ProfileCreationForm
    add_fieldsets = (
        (None, {'fields': ('name', 'email', 'phone', 'password1', 'password2')}),
    )
    readonly_fields = ('date_joined',)
    ordering = ('-date_joined',)


@admin.register(UserFilter)
class UserFilter(admin.ModelAdmin):
    list_display = ['user', 'blocked']

@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ['user', 'plan']

@admin.register(Plan)
class Plan(admin.ModelAdmin):
    list_display = ['name', 'period_days']


admin.site.unregister(Group)
