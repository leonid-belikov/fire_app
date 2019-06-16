from django import forms
from .models import *


class MoneyMovementForm(forms.ModelForm):

    class Meta:
        model = MoneyMovement
        fields = ['date', 'amount', 'purpose', 'tag', 'direction', 'comment']
