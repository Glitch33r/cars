from django import template
register = template.Library()

from main.models import (
    Mark,
    Model,
    Location,
    Gearbox
)


@register.simple_tag(name='marks')
def mark_list():
    return Mark.objects.all()


@register.simple_tag(name='locations')
def location_list():
    return Location.objects.all()


@register.simple_tag(name='gearboxs')
def gearbox_list():
    return Gearbox.objects.all()
