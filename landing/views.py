from django.shortcuts import render
from django.http import JsonResponse
from .forms import MoneyMovementForm, MMPlanForm
from .models import MoneyMovement
from .tabs.plan import *
from django.utils.timezone import now
import datetime


MONTHS = [
    {'value': 1, 'name': 'Январь', 'r_date': 'января', 'current': False},
    {'value': 2, 'name': 'Февраль', 'r_date': 'февраля', 'current': False},
    {'value': 3, 'name': 'Март', 'r_date': 'марта', 'current': False},
    {'value': 4, 'name': 'Апрель', 'r_date': 'апреля', 'current': False},
    {'value': 5, 'name': 'Май', 'r_date': 'мая', 'current': False},
    {'value': 6, 'name': 'Июнь', 'r_date': 'июня', 'current': False},
    {'value': 7, 'name': 'Июль', 'r_date': 'июля', 'current': False},
    {'value': 8, 'name': 'Август', 'r_date': 'августа', 'current': False},
    {'value': 9, 'name': 'Сентябрь', 'r_date': 'сентября', 'current': False},
    {'value': 10, 'name': 'Октябрь', 'r_date': 'октября', 'current': False},
    {'value': 11, 'name': 'Ноябрь', 'r_date': 'ноября', 'current': False},
    {'value': 12, 'name': 'Декабрь', 'r_date': 'декабря', 'current': False},
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
                'dates': dates,
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

        for mm in mms:
            mm['date'] = mm['date'].strftime("%d.%m.%Y")
        return mms

    def get_dates_for_filter(self):
        dates_set = set(MoneyMovement.objects.filter(
            date__month=self.month,
            date__year=self.year
        ).values_list('date', flat=True))
        res = []
        for date in sorted(dates_set):
            row = {
                'year': date.year,
                'month': date.month,
                'day': date.day
            }
            res.append(row)
        return res

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

    if request.method == 'POST' and request.POST.get('day') and request.POST.get('day') is not None:
        day = request.POST.get('day')
        month = request.POST.get('month')
        year = request.POST.get('year')
        str_filter_date = "%s-%s-%s" % (year, month, day)
        filter_date = datetime.datetime.strptime(str_filter_date, "%Y-%m-%d")
        values = MoneyMovement.objects.filter(date=filter_date).order_by('purpose').values()
        render_month = ''
        for m in MONTHS:
            if m['value'] == int(month):
                render_month = m['r_date']

        mms = [mm for mm in values]
        day_amounts = get_day_amounts(filter_date)
        render_date = "%s %s %s г." % (request.POST.get('day'), render_month, year)

        return render(request, 'landing/mm_table.html',
                      {
                          'mms': mms,
                          'day_amounts': day_amounts,
                          'render_date': render_date
                      })

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
        'dates': dates
    })
