from django.shortcuts import render
from django.http import JsonResponse
from .forms import MoneyMovementForm, MMPlanForm
from .models import MoneyMovement
from .tabs.plan import *
from django.utils.timezone import now


class MainData:

    def __init__(self, month, year):
        self.current_month = now().month if month is None else month
        self.current_year = now().year if year is None else year

    def get_last_mms(self):
        # пять последних записей для отображения на странице
        values = MoneyMovement.objects.filter(
            date__month=self.current_month,
            date__year=self.current_year
        ).reverse()[:5].values()
        mms = [mm for mm in values]

        return mms

    def get_dates_for_filter(self):
        return set(MoneyMovement.objects.filter(
            date__month=self.current_month,
            date__year=self.current_year
        ).values_list('date', flat=True))

    def get_total_amount(self):
        total_amount = 0
        for rec in MoneyMovement.objects.filter(
            date__month=self.current_month,
            date__year=self.current_year
        ).values('amount', 'direction'):
            if rec['direction'] == 'income':
                total_amount += rec['amount']
            elif rec['direction'] == 'cost':
                total_amount -= rec['amount']

        return total_amount


def landing(request):

    ctx = get_context()

    return render(request, 'landing/landing.html', ctx)


def get_context(month=None, year=None, url=None):
    main_data = MainData(month, year)

    if not url or url == 'landing/tab_reg.html':
        mms = main_data.get_last_mms()
        dates = main_data.get_dates_for_filter()
        total_amount = main_data.get_total_amount()
        context = {
            'text': 'Запишем фактические доходы и расходы',
            'form': MoneyMovementForm(None),
            'mms': mms,
            'total_amount': total_amount,
            'dates': sorted([str(date) for date in dates])
        }
    elif url == 'landing/tab_plan.html':
        context = {
            'text': 'Распланируем доходы и расходы',
            'form': MMPlanForm(None),
            'total_plan_amount': get_total_plan_amount()['total_plan_amount'],
            'total_plan_income': get_total_plan_amount()['total_plan_income'],
            'total_plan_cost': get_total_plan_amount()['total_plan_cost'],
            'incomes': get_plan_incomes(),
            'costs': get_plan_costs()
        }
    elif url == 'landing/tab_total.html':
        context = {
            'text': 'Посмотрим, как распеределены бабосы'
        }
    else:
        context = {}

    return context


def add_mm(request):

    form = MoneyMovementForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        # return JsonResponse({'html': html, 'total_amount': get_total_amount()})
        return render(request, 'landing/mm_table.html', {'mms': MainData().get_last_mms()})

    return JsonResponse({'Error': 'invalid form'})


def filter_by_date(request):

    if request.method == 'POST' and request.POST['date'] is not None:
        filter_date = request.POST['date']
        values = MoneyMovement.objects.filter(date=filter_date).values()
        mms = [mm for mm in values]

        # return JsonResponse({'items': mms})
        return render(request, 'landing/mm_table.html', {'mms': mms})

    return JsonResponse({'Error': 'Invalid request'})


def reload_total_amount(request):
    dates_set = set(MoneyMovement.objects.values_list('date', flat=True))

    return JsonResponse({
        'total_amount': get_total_amount(),
        'dates': sorted([str(date) for date in dates_set])
    })


def render_tab(request):
    template = request.POST['template']
    month = now().month if request.POST['month'] is None else request.POST['month']
    year = now().year if request.POST['year'] is None else request.POST['year']
    ctx = get_context(month, year, template)

    return render(request, template, ctx)
