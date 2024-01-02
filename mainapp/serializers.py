from rest_framework import serializers
from .models import Product, Purchase
from accountsapp.models import Client
from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'name', 'text', 'price', 'count_in_storage']

'''
class ClientSerializer(serializers.ModelSerializer):
    
    user = serializers.PrimaryKeyRelatedField(read_only = True)

    class Meta:
        model = Client
        fields = ['user', 'wallet']
'''
'''
class PurchaseSerializer(serializers.ModelSerializer): # для отримання Покупки за даними Клієнта

    user = ClientSerializer()
    product = ProductSerializer(many=True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'count']
'''


class PurchaseSerializer(serializers.ModelSerializer):    

    product = ProductSerializer(read_only = True, many=True)
    
    class Meta:
        model = Purchase
        fields = ['id', 'user', 'product', 'count']


class UserSerializer(serializers.ModelSerializer):

    purchase = serializers.StringRelatedField(read_only = True, many=True)

    class Meta:
        model = User
        fields = ['username', 'purchase']


class ClientSerializer(serializers.ModelSerializer): # для отримання Клієнта з покупками

    purchase_set = serializers.SerializerMethodField()

    def get_purchase_set(self, obj):
        purchases = obj.purchase_set.all()
        serialized_purchases = []
        for purchase in purchases:
            serialized_purchases.append({
                'id': purchase.id,
                'purchase': purchase,
                'count': purchase.count
            })
        return serialized_purchases
    
    user = serializers.PrimaryKeyRelatedField(read_only = True)

    class Meta:
        model = Client
        fields = ['user', 'wallet', 'purchase_set']