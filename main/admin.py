from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Profile)


class MarkInline(admin.TabularInline):
    model = Mark
    extra = 0


class ModelAdmin(admin.ModelAdmin):
    inlines = [MarkInline]


admin.site.register(Model, ModelAdmin)
admin.site.register(Location)

