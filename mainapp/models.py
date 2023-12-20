from django.db import models
from accountsapp.models import Client


class Product(models.Model):
    name = models.CharField(max_length=255)
    text = models.TextField(null=True, blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)
    count_in_storage = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

class Purchase(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE, null = True, blank = True)
    create_at = models.DateTimeField(auto_now_add=True)
    product = models.ManyToManyField(Product)
    count = models.IntegerField(null=True, blank=True)

    def __str__(self) -> str:
        product_names = ', '.join([product.name for product in self.product.all()])
        return f"{self.user} - {product_names}"

class Return(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, null = True, blank = True)
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.purchase.user} - {self.create_at}"

