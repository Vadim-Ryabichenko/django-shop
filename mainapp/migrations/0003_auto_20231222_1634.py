# Generated by Django 4.2.8 on 2023-12-22 16:34

from django.db import migrations


def create_2_prod(apps, schema_editor):
    Product = apps.get_model('mainapp', 'Product') 
    Product.objects.create(name='Water', text = 'Water for light-training', price = 15, count_in_storage = 50)
    Product.objects.create(name='Coffee', text = 'Coffee for light-predtraining', price = 25, count_in_storage = 30)
    

class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0002_alter_product_price_alter_purchase_create_at_and_more'),
    ]

    operations = [
        migrations.RunPython(create_2_prod, lambda x, y: None)
    ]
