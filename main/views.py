from django.http import JsonResponse
from django.shortcuts import render
from .forms import FilterForm
# Create your views here.
from seed_db.fk_tables import seed_location, seed_body, seed_color, seed_fuel, seed_gearbox, seed_mark, seed_model
from django.views.decorators.http import require_GET


def filter_form_render_view(request):
    filterForm = FilterForm()
    return render(request, 'filter_form.html', {
        'form': filterForm
    })


def filter_handle(request):
    print(request.GET.dict())
    pass


@require_GET
def seed_db(request):
    seed_fuel()
    seed_gearbox()
    seed_body()
    seed_color()
    seed_location()
    seed_mark()
    seed_model()
    return JsonResponse(dict(status='success'))
