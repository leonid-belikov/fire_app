from django.shortcuts import render
from django.http import JsonResponse
from django.core.serializers import serialize
from collections import ChainMap
from .forms import SubscriberForm
from .models import Subscriber


def landing(request):

    form = SubscriberForm(None)
    users = [user for user in Subscriber.objects.all()]

    return render(request, 'landing/landing.html', locals())


def reload_users_table():

    values = Subscriber.objects.all().values()
    resp_list = list(values)

    return JsonResponse(resp_list, safe=False)


def add_user(request):

    form = SubscriberForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return reload_users_table()

    return JsonResponse({'Error': 'invalid form'})
