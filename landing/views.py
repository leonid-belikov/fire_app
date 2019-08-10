from django.shortcuts import render
from django.http import JsonResponse
from .forms import MoneyMovementForm, MMPlanForm
from .models import MoneyMovement
from .tabs.plan import *
from django.utils.timezone import now
import datetime


MONTHS = [
    {'value': 1, 'name': 'Январь', 'current': False},
    {'value': 2, 'name': 'Февраль', 'current': False},
    {'value': 3, 'name': 'Март', 'current': False},
    {'value': 4, 'name': 'Апрель', 'current': False},
    {'value': 5, 'name': 'Май', 'current': False},
    {'value': 6, 'name': 'Июнь', 'current': False},
    {'value': 7, 'name': 'Июль', 'current': False},
    {'value': 8, 'name': 'Август', 'current': False},
    {'value': 9, 'name': 'Сентябрь', 'current': False},
    {'value': 10, 'name': 'Октябрь', 'current': False},
    {'value': 11, 'name': 'Ноябрь', 'current': False},
    {'value': 12, 'name': 'Декабрь', 'current': False},
]


class MainData:

    def __init__(self, request=None):
        self.request = request
        self.month = self.request.POST['month'] if self.request and self.request.POST.get('month') else now().month
        self.year = self.request.POST['year'] if self.request and self.request.POST.get('year') else now().year

    def get_context(self):
        url = self.request.POST['template'] if self.request and self.request.POST.get('template') else None

        if not url or url == 'landing/tab_reg.html':
            mms = self.get_last_mms()
            dates = self.get_dates_for_filter()
            total_amount = self.get_total_amount()
            context = {
                'text': 'Запишем фактические доходы и расходы',
                'form': MoneyMovementForm(None),
                'mms': mms,
                'total_amount': total_amount,
                'dates': sorted([str(date) for date in dates]),
                'month_list': self.get_month_list(),
                'current_year': self.year,
                # 'current_month': self.month
            }
        elif url == 'landing/tab_plan.html':
            context = {
                'text': 'Распланируем доходы и расходы',
                'form': MMPlanForm(None),
                'total_plan_amount': get_total_plan_amount()['total_plan_amount'],
                'total_plan_income': get_total_plan_amount()['total_plan_income'],
                'total_plan_cost': get_total_plan_amount()['total_plan_cost'],
                'incomes': get_plan_incomes(),
                'costs': get_plan_costs(),
                # 'current_year': self.year,
                # 'current_month': self.month
            }
        elif url == 'landing/tab_total.html':
            context = {
                'text': 'Посмотрим, как распеределены бабосы',
                # 'current_year': self.year,
                # 'current_month': self.month
            }
        else:
            context = {}

        return context

    def get_last_mms(self):
        # пять последних записей для отображения на странице
        values = MoneyMovement.objects.filter(
            date__month=self.month,
            date__year=self.year
        ).reverse()[:5].values()
        mms = [mm for mm in values]

        return mms

    def get_dates_for_filter(self):
        return set(MoneyMovement.objects.filter(
            date__month=self.month,
            date__year=self.year
        ).values_list('date', flat=True))

    def get_total_amount(self):
        total_amount = 0
        for rec in MoneyMovement.objects.filter(
            date__month=self.month,
            date__year=self.year
        ).values('amount', 'direction'):
            if rec['direction'] == 'income':
                total_amount += rec['amount']
            elif rec['direction'] == 'cost':
                total_amount -= rec['amount']

        return total_amount

    def get_month_list(self):
        month_list = MONTHS[:]
        for month in month_list:
            if month['value'] == self.month:
                month['current'] = True
        return month_list


def landing(request):
    main_data = MainData(request)
    ctx = main_data.get_context()

    return render(request, 'landing/landing.html', ctx)


def add_mm(request):
    main_data = MainData(request)

    form = MoneyMovementForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'landing/mm_table.html', {'mms': main_data.get_last_mms()})

    return JsonResponse({'Error': 'invalid form'})


def filter_by_date(request):

    if request.method == 'POST' and request.POST.get('date') and request.POST.get('date') is not None:
        filter_date = datetime.datetime.strptime(request.POST['date'], "%Y-%m-%d")
        values = MoneyMovement.objects.filter(date=filter_date).values()
        mms = [mm for mm in values]
        day_amounts = get_day_amounts(filter_date)

        return render(request, 'landing/mm_table.html', {'mms': mms, 'day_amounts': day_amounts})

    return JsonResponse({'Error': 'Invalid request'})


def get_day_amounts(date):
    first_date = "%s-%s-01" % (date.year, date.month)
    # сумма за день
    day_amount = 0
    for rec in MoneyMovement.objects.filter(date=date).values('amount', 'direction'):
        if rec['direction'] == 'income':
            day_amount += rec['amount']
        elif rec['direction'] == 'cost':
            day_amount -= rec['amount']
    # сумма на утро
    morning_amount = 0
    for rec in MoneyMovement.objects.filter(date__range=[first_date, date]).\
            exclude(date=date).values('amount', 'direction'):
        if rec['direction'] == 'income':
            morning_amount += rec['amount']
        elif rec['direction'] == 'cost':
            morning_amount -= rec['amount']
    # сумма итого
    result_amount = morning_amount + day_amount

    return {
        'start': morning_amount,
        'delta': day_amount,
        'total': result_amount
    }


def render_tab(request):
    if request.method == 'POST' and request.POST.get('template') and request.POST.get('template') is not None:
        template = request.POST['template']
        main_data = MainData(request)
        ctx = main_data.get_context()

        return render(request, template, ctx)

    return JsonResponse({'Error': 'Invalid request'})


def reload_total_amount(request):
    main_data = MainData(request)
    dates = main_data.get_dates_for_filter()
    total_amount = main_data.get_total_amount()

    return JsonResponse({
        'total_amount': total_amount,
        'dates': sorted([str(date) for date in dates])
    })
