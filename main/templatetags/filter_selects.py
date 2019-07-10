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
    return Mark.objects.all().order_by('name')


@register.simple_tag(name='models')
def model_list():
    return Model.objects.all().order_by('name')


@register.simple_tag(name='locations')
def location_list():
    return Location.objects.all().order_by('name')


@register.simple_tag(name='gearboxs')
def gearbox_list():
    return Gearbox.objects.all()
