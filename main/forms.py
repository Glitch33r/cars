from .models import Filter
from django.forms import ModelForm


class FilterForm(ModelForm):
    class Meta:
        model = Filter
        fields = '__all__'
