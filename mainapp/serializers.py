from rest_framework import serializers
from .models import Product, Purchase, Return
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


class PurchaseSerializer(serializers.ModelSerializer):    

    product = ProductSerializer(read_only = True, many=True)
    user = ClientSerializer(read_only = True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'count']


class UserSerializer(serializers.ModelSerializer):

    purchase = serializers.StringRelatedField(read_only = True, many=True)

    class Meta:
        model = User
        fields = ['username', 'purchase']


class ReturnSerializer(serializers.ModelSerializer):

    purchase = PurchaseSerializer(read_only = True)

    class Meta:
        model = Return
        fields = ['id', 'purchase']