"""test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from landing import views
from landing.tabs import plan

urlpatterns = [
    path('pupu/', views.landing, name='landing'),
    path('add_mm/', views.add_mm, name='add_mm'),
    path('filter_by_date/', views.filter_by_date, name='filter_by_date'),
    path('tab/', views.render_tab, name='render_tab'),
    path('reload_total_amount/', views.reload_total_amount, name='reload_total_amount'),
    path('add_mmplan/', plan.add_mmplan, name='add_mmplan'),
    path('select_date/', views.render_tab, name='render_tab'),
    path('reload_mm_row/', views.reload_mm_row, name='reload_mm_row'),
    path('delete_mm_row/', views.delete_mm_row, name='delete_mm_row'),
]
