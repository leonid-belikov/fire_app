from django.shortcuts import render
from django.http import JsonResponse
from ..forms import MMPlanForm
from ..models import MMPlan


def add_mmplan(request):

    form = MMPlanForm(request.POST or None)
    error_msg = 'request.method: %s' % request.method

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            ctx = {
                'total_plan_income': get_total_plan_amount()['total_plan_income'],
                'total_plan_cost': get_total_plan_amount()['total_plan_cost'],
                'incomes': get_plan_incomes(),
                'costs': get_plan_costs()
            }
            return render(request, 'landing/mm_plan_table.html', ctx)
        else:
            error_msg = 'invalid form: %s' % form.errors

    return JsonResponse({'Error': error_msg})


def get_plan_incomes():

    values = MMPlan.objects.filter(direction='income').values()
    incomes = [income for income in values]

    return incomes


def get_plan_costs():

    values = MMPlan.objects.filter(direction='cost').values()
    costs = [cost for cost in values]

    return costs


def get_total_plan_amount():
    total_plan_amount = 0
    total_plan_income = 0
    total_plan_cost = 0
    for rec in MMPlan.objects.values('amount', 'direction'):
        if rec['direction'] == 'income':
            total_plan_income += rec['amount']
            total_plan_amount += rec['amount']
        elif rec['direction'] == 'cost':
            total_plan_cost += rec['amount']
            total_plan_amount -= rec['amount']

    return {
        'total_plan_amount': total_plan_amount,
        'total_plan_income': total_plan_income,
        'total_plan_cost': total_plan_cost
    }
