from django import forms
from .models import *


class MoneyMovementForm(forms.ModelForm):

    class Meta:
        model = MoneyMovement
        fields = ['date', 'amount', 'purpose', 'category', 'direction', 'comment']


class MMPlanForm(forms.ModelForm):

    class Meta:
        model = MMPlan
        fields = ['date', 'amount', 'purpose', 'category', 'direction', 'comment']
