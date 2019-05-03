from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from .forms import SubscriberForm
from .models import Subscriber


def landing(request):

    form = SubscriberForm(None)
    users = [user for user in Subscriber.objects.all()]

    return render(request, 'landing/landing.html', locals())


def reload_users_table():

    resp_text = {}

    for user in Subscriber.objects.all():
        resp_text[user.id] = {
            'name': user.name,
            'email': user.email
        }

    return JsonResponse(resp_text)


def add_user(request):

    form = SubscriberForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return reload_users_table()

    return JsonResponse({'Error': 'invalid form'})
