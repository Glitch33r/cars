from django.contrib import admin
from django.utils.html import format_html

from .models import *


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('model', 'engine', 'gearbox', 'fuel', 'price', 'mileage', 'show_rst_link', 'show_ab_link', 'createdAt', 'updatedAt', 'last_site_updatedAt')

    def show_rst_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.rst_link)
    show_rst_link.short_description = "rst link"

    def show_ab_link(self, obj):
        return format_html("<a href='{url}' target='_blank'>{url}</a>", url=obj.ab_link)
    show_ab_link.short_description = "ab link"


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'mark')


admin.site.register(Profile)
admin.site.register(Mark)
admin.site.register(Gearbox)
admin.site.register(Location)
admin.site.register(Fuel)
admin.site.register(Color)
admin.site.register(SellerPhone)
admin.site.register(Body)
