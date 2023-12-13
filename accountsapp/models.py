from django.db import models
from django.contrib.auth.models import User


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wallet = models.DecimalField(decimal_places=2, max_digits=12, default=10000)

    def __str__(self):
        return f'{self.user} {self.wallet}'