from django.shortcuts import render
from django.http import JsonResponse
from .models import MoneyMovement
from .forms import MoneyMovementForm
from .tabs.plan import *
from .main_data import MainData


def landing(request):
    main_data = MainData(request)
    ctx = main_data.get_context()

    return render(request, 'landing/landing.html', ctx)


def add_mm(request):
    main_data = MainData(request)
    print(request.POST)

    form = MoneyMovementForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return render(request, 'landing/mm_table.html', {
                          'mms': main_data.get_day_mms(),
                          'render_date': main_data.get_render_date(),
                          'day_amounts': main_data.get_day_amounts()
                      })

    return JsonResponse({'Error': 'invalid form'})


def filter_by_date(request):

    main_data = MainData(request)

    return render(request, 'landing/mm_table.html',
                  {
                      'mms': main_data.get_day_mms(),
                      'day_amounts': main_data.get_day_amounts(),
                      'render_date': main_data.get_render_date()
                  })


def render_tab(request):
    template = request.POST['template']
    print(request.POST)
    main_data = MainData(request)
    ctx = main_data.get_context()

    return render(request, template, ctx)


def reload_total_amount(request):
    main_data = MainData(request)
    dates = main_data.get_str_dates_for_filter()
    total_amount = main_data.get_total_amount()

    return JsonResponse({
        'total_amount': total_amount,
        'dates': dates
    })


def reload_mm_row(request):
    row = MoneyMovement.objects.get(id=request.POST['id'])
    exclude_fields = {'csrfmiddlewaretoken', 'id'}
    for name in request.POST:
        if name not in exclude_fields:
            setattr(row, name, request.POST[name])
    row.save()
    # TODO: поискать способ сделать поумнее
    row_dict = {
        'id': row.id,
        'direction': row.direction,
        'amount': row.amount,
        'purpose': row.purpose,
        'category': row.category,
        'comment': row.comment
    }

    return render(request, 'landing/mm_table_row.html', {'mm': row_dict})


def delete_mm_row(request):
    row_id = request.POST.get('id')
    if row_id:
        date = MoneyMovement.objects.get(id=row_id).date
        MoneyMovement.objects.filter(id=row_id).delete()
        main_data = MainData(date=date)
        return render(request, 'landing/mm_table.html', {
                          'mms': main_data.get_day_mms(),
                          'render_date': main_data.get_render_date(),
                          'day_amounts': main_data.get_day_amounts()
                      })
