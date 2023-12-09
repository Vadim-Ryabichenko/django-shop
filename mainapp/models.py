from django.db import models
from accountsapp.models import Profile


class Product(models.Model):
    name = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12)
    count_in_storage = models.IntegerField(null=True, blank=True)


class Purchase(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null = True, blank = True)
    create_at = models.DateField(auto_now_add=True)
    product = models.ManyToManyField(Product)
    count = models.IntegerField(null=True, blank=True)


class Return(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null = True, blank = True)
    create_at = models.DateField(auto_now_add=True)