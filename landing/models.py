from django.db import models
from django.utils.timezone import now


class Subscriber(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.id)


class MoneyMovement(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    date = models.DateField(default=now)
    purpose = models.CharField(max_length=50)
    tag = models.CharField(max_length=25)
    direction = models.CharField(max_length=10)
    comment = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)
    changed = models.DateField(auto_now=True)

    def __str__(self):
        if self.direction not in ('income', 'cost'):
            return 'Wrong direction!'
        dir_string = 'Поступление' if self.direction == 'income' else 'Расход'
        return '%s (%s) на %s руб. от %s' % (dir_string, self.purpose, self.amount, str(self.date))

    class Meta:
        ordering = ['date', 'id']
