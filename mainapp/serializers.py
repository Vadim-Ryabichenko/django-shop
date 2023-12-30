from rest_framework import serializers
from .models import Product, Purchase
from accountsapp.models import Client
from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'text', 'price', 'count_in_storage']


class ClientSerializer(serializers.ModelSerializer):
    
    user = serializers.PrimaryKeyRelatedField(read_only = True)

    class Meta:
        model = Client
        fields = ['user', 'wallet']

'''
class PurchaseSerializer(serializers.ModelSerializer):    

    product = ProductSerializer(read_only = True, many=True)
    user = serializers.PrimaryKeyRelatedField(read_only = True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'count']
'''


class PurchaseSerializer(serializers.ModelSerializer):  # це для завдання 3

    user = ClientSerializer()
    
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'count']

