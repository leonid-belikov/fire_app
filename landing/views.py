from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.response import TemplateResponse
from django.template import Template, Context
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import MoneyMovementForm
from .models import MoneyMovement


@ensure_csrf_cookie
def landing(request):

    form = MoneyMovementForm(None)
    mms = get_last_mms()
    total_amount = get_total_amount()
    dates_set = set(MoneyMovement.objects.values_list('date', flat=True))
    dates = sorted([str(date) for date in dates_set])

    return render(request, 'landing/landing.html', locals())


def add_mm(request):

    form = MoneyMovementForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return JsonResponse({'items': get_last_mms(), 'total_amount': get_total_amount()})

    return JsonResponse({'Error': 'invalid form'})


def filter_by_date(request):

    if request.method == 'POST' and request.POST['date'] is not None:
        filter_date = request.POST['date']
        values = MoneyMovement.objects.filter(date=filter_date).values()
        mms = [mm for mm in values]

        return JsonResponse({'items': mms})

    return JsonResponse({'Error': 'Invalid request'})


def get_last_mms():

    # пять последних записей для отображения на странице
    values = MoneyMovement.objects.all().reverse()[:5].values()
    mms = [mm for mm in values]

    return mms


def get_total_amount():
    total_amount = 0
    for rec in MoneyMovement.objects.values('amount', 'direction'):
        if rec['direction'] == 'income':
            total_amount += rec['amount']
        elif rec['direction'] == 'cost':
            total_amount -= rec['amount']

    return total_amount


def planning(request):
    info = request.POST['tab_id']

    return render_to_response('landing/plan.html', {'info': info})
