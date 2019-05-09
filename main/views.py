from django.shortcuts import render
from .forms import FilterForm
# Create your views here.


def filter_form_render_view(request):
    filterForm = FilterForm()
    return render(request, 'filter_form.html', {
        'form': filterForm
    })


def filter_handle(request):
    print(request.GET.dict())
    pass
