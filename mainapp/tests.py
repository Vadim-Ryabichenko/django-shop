from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Purchase, Product, Return
from accountsapp.models import Client
from .views import PurchaseListView, ReturnConfirmView, PurchaseModelViewSet, ReturnModelViewSet
from decimal import Decimal
from django.contrib import messages
from django.contrib.messages import get_messages
from mainapp.forms import ProductForm
from datetime import timedelta
from rest_framework.test import APITestCase, force_authenticate
from .serializers import ProductSerializer, PurchaseSerializer, ReturnSerializer
from rest_framework.serializers import ValidationError
from rest_framework.test import APIRequestFactory
import json
from rest_framework.authtoken.models import Token
from django.utils import timezone


class UnitPurchaseListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Test Product', count_in_storage=10, price=10)
        self.client = Client.objects.create(user=self.user, wallet=100)

    def test_purchase_creation(self):
        request = self.factory.post(reverse('purchases'), {'pk': self.product.pk, 'count': '1'})
        request.user = self.user
        request._messages = messages.storage.default_storage(request)
        response = PurchaseListView.as_view()(request)
        self.assertEqual(response.status_code, 302)  
        purchase = Purchase.objects.get(user__user=self.user)
        self.assertEqual(purchase.count, 1)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.count_in_storage, 9)  
        user = Client.objects.get(user=self.user)
        self.assertEqual(user.wallet, Decimal('90.00')) 


class IntegrationPurchaseListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='Test Product', count_in_storage=10, price=10)
        self.client_instance = Client.objects.create(user=self.user, wallet=20)

    def test_purchase_creation(self):
        login = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login)
        response = self.client.post(reverse('purchases'), {'pk': self.product.pk, 'count': '1'}, follow=True)
        self.assertEqual(response.status_code, 200)
        purchases = Purchase.objects.filter(user__user=self.user)
        self.assertEqual(purchases.count(), 1)
        product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(product.count_in_storage, 9)
        user = Client.objects.get(user=self.user)
        self.assertEqual(user.wallet, 10)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Purchase completed successfully')

    def test_not_enough_products_in_storage(self):
        login = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login)
        response = self.client.post(reverse('purchases'), {'pk': self.product.pk, 'count': '20'}, follow=True)
        self.assertEqual(response.status_code, 200)
        purchases = Purchase.objects.filter(user__user=self.user)
        self.assertEqual(purchases.count(), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Not enough products in storage')
    
    def test_not_enough_money(self):
        login = self.client.login(username='testuser', password='testpass')
        self.assertTrue(login)
        initial_purchase_count = Purchase.objects.filter(user__user=self.user).count()
        response = self.client.post(reverse('purchases'), {'pk': self.product.pk, 'count': '8'}, follow=True)
        self.assertEqual(response.status_code, 200)
        final_purchase_count = Purchase.objects.filter(user__user=self.user).count()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(final_purchase_count, initial_purchase_count)
        self.assertEqual(str(messages[0]), 'You dont have enough money')


class ProductPageViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='MyProduct', count_in_storage=10, price=10)

    def test_get_product_page(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('product_detail', args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MyProduct')
        self.assertIn('product', response.context)
        self.assertEqual(response.context['product'], self.product)

    def test_get_nonexistent_product_page(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('product_detail', args=[100])  
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ProductUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(name='TestProduct', text='Test text', price=10, count_in_storage=5)

    def login_user(self):
        self.client.login(username='testuser', password='testpass')

    def test_get_product_update_view(self):
        self.login_user()
        url = reverse('update_product', args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productupdate.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ProductForm)

    def test_post_product_update_view(self):
        self.login_user()
        data = {
            'name': 'UpdatedProduct',
            'text': 'Updated text',
            'count_in_storage': 8,
            'price': 15,
        }
        url = reverse('update_product', args=[self.product.pk])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(response.url, '/products')  
        updated_product = Product.objects.get(pk=self.product.pk)
        self.assertEqual(updated_product.name, 'UpdatedProduct')
        self.assertEqual(updated_product.text, 'Updated text')
        self.assertEqual(updated_product.count_in_storage, 8)
        self.assertEqual(updated_product.price, 15)


class ProductCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def login_user(self):
        self.client.login(username='testuser', password='testpass')

    def test_get_product_create_view(self):
        self.login_user()
        url = reverse('create_product')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'productcreate.html')
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], ProductForm)

    def test_post_product_create_view(self):
        self.login_user()
        data = {
            'name': 'NewProduct',
            'text': 'It new product',
            'count_in_storage': 10,
            'price': 20,
        }
        url = reverse('create_product')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  
        self.assertEqual(response.url, '/products')  
        created_product = Product.objects.last()
        self.assertEqual(created_product.name, 'NewProduct')


class ReturnListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.purchase = Purchase.objects.create(create_at=timezone.now() - timedelta(seconds=100))

    def test_return_list_view_post_success(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('returns'), {'purchase_id': self.purchase.id})
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Return.objects.count(), 1)
        self.assertRedirects(response, reverse('returns'))

    def test_return_list_view_post_failure(self):
        self.client.login(username='testuser', password='testpassword')
        self.purchase.create_at = timezone.now() - timedelta(seconds=200)
        self.purchase.save()
        response = self.client.post(reverse('returns'), {'purchase_id': self.purchase.id})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Return.objects.count(), 0)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Return is no longer possible')
        self.assertRedirects(response, reverse('purchases'))


class ReturnRejectViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.return_obj = Return.objects.create()

    def test_return_reject_view_post_success(self):
        self.client.login(username='testuser', password='testpassword')
        return_id = self.return_obj.id
        print(f'check_check: {return_id}')
        response = self.client.post(reverse('return_reject', args=[return_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Return.objects.filter(id=return_id).exists())
        self.assertRedirects(response, reverse('returns'))


class ProductSerializerTest(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(**{
            'name': 'testproduct',
            'text': 'testtext',
            'price': '45.00',
            'count_in_storage': '13'
        })

    def test_product_valid_serializer(self):
        product = Product.objects.get(pk = self.product1.pk)
        serializer = ProductSerializer(product)
        data = serializer.data
        self.assertEqual(data['name'], 'testproduct')
        self.assertEqual(data['text'], 'testtext')
        self.assertEqual(data['price'], '45.00')
        self.assertEqual(data['count_in_storage'], 13)

    def test_product_invalid_serializer(self):
        invalid_product_data = {
            'price': '18.00',
        }
        with self.assertRaises(ValidationError):
            serializer = ProductSerializer(data=invalid_product_data)
            serializer.is_valid(raise_exception=True)
   

class PurchaseSerializerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser', password='testpassword')
        self.client1 = Client.objects.create(user = self.user1)
        self.product1 = Product.objects.create(name='testproduct', text='testtext', price='45.00', count_in_storage=13)
        self.purchase1 = Purchase.objects.create(user=self.client1, count=2)
        self.purchase1.product.add(self.product1)

    def test_purchase_valid_serializer(self):
        purchase = Purchase.objects.last()
        serializer = PurchaseSerializer(purchase)
        data = serializer.data
        self.assertEqual(data['id'], self.purchase1.id)
        self.assertEqual(data['user']['user'], 14)
        self.assertEqual(data['product'][0]['name'], 'testproduct')
        self.assertEqual(data['count'], 2)

    def test_purchase_invalid_serializer(self):
        invalid_purchase_data = {
            'count': 'bagato'
        }
        with self.assertRaises(ValidationError):
            serializer = PurchaseSerializer(data=invalid_purchase_data)
            serializer.is_valid(raise_exception=True)


class ReturnSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='lala', password='lalapass')
        self.client = Client.objects.create(user=self.user)
        self.product = Product.objects.create(name='lalaproduct', text='lalatext', price='22.00', count_in_storage=13)
        self.purchase = Purchase.objects.create(user=self.client, count=2)
        self.purchase.product.add(self.product)
        self.return1 = Return.objects.create(purchase=self.purchase)

    def test_return_valid_serializer(self):
        return_obj = Return.objects.get(pk=self.return1.pk)
        serializer = ReturnSerializer(return_obj)
        data = serializer.data
        self.assertEqual(data['id'], self.return1.id)
        self.assertEqual(data['purchase']['id'], self.purchase.id)
        self.assertEqual(data['purchase']['user']['user'], self.user.pk)  
        self.assertEqual(data['purchase']['product'][0]['name'], 'lalaproduct')
        self.assertEqual(data['purchase']['count'], 2)


class ReturnConfirmViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client.objects.create(user=self.user, wallet=100)
        self.product = Product.objects.create(name='Test Product', price=10, count_in_storage=20)
        self.purchase = Purchase.objects.create(user=self.client, count=2)
        self.purchase.product.set([self.product])
        self.return_obj = Return.objects.create(purchase=self.purchase)

    def test_post_method(self):
        url = reverse('return_confirm', args=[self.return_obj.id])
        request = self.factory.post(url)
        request.user = self.user
        response = ReturnConfirmView.as_view()(request, return_id=self.return_obj.id)
        self.assertEqual(Return.objects.filter(id=self.return_obj.id).exists(), False)
        self.assertEqual(Purchase.objects.filter(id=self.purchase.id).exists(), False)
        updated_client = Client.objects.get(id=self.client.id)
        self.assertEqual(updated_client.wallet, self.client.wallet + self.purchase.count * self.product.price)
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.count_in_storage, self.product.count_in_storage + self.purchase.count)
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(response.url, reverse('returns'))
        

class PurchaseModelViewSetTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client = Client.objects.create(user=self.user, wallet=100)
        self.product = Product.objects.create(name='Test Product', price=10, count_in_storage=20)
        self.url = '/api/purchas/'  

    def test_create_purchase_successful(self):
        data = {
            'user': {'user': self.user.id},
            'product': [{'id': self.product.id}],
            'count': 2
        }
        request = self.factory.post(self.url, json.dumps(data), content_type='application/json')
        force_authenticate(request, user=self.user)
        response = PurchaseModelViewSet.as_view({'post': 'create'})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Purchase completed successfully')
        purchase = Purchase.objects.last()
        self.assertEqual(purchase.user, self.client)
        self.assertEqual(purchase.product.first(), self.product)
        self.assertEqual(purchase.count, 2)
        self.client.refresh_from_db()
        self.assertEqual(self.client.wallet, 80)
        self.product.refresh_from_db()
        self.assertEqual(self.product.count_in_storage, 18)


class ReturnModelViewSetTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.purchase = Purchase.objects.create(create_at=timezone.now() - timedelta(seconds=100))

    def test_create_return(self):
        view = ReturnModelViewSet.as_view({'post': 'create'})
        data = {'purchase': {'id': self.purchase.id}}
        request = self.factory.post('/returns/', data, format='json')
        request.user = self.user
        force_authenticate(request, user=self.user, token=self.token.key)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Return.objects.count(), 1)


