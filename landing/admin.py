from django.contrib import admin
from .models import *


class MoneyMovementAdmin(admin.ModelAdmin):
    list_display = [field.name for field in MoneyMovement._meta.fields]
    list_filter = ['date']

    class Meta:
        model = MoneyMovement


admin.site.register(MoneyMovement, MoneyMovementAdmin)
