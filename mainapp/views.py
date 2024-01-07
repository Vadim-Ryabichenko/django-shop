from .models import Product, Return, Purchase
from accountsapp.models import Client
from django.views.generic import ListView, TemplateView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import ProductForm
from django.shortcuts import redirect
from django.contrib import messages
from datetime import datetime, timezone
from django.db.models import F
from .serializers import ProductSerializer, ReturnSerializer, PurchaseSerializer, ClientSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from mainapp.permissions import ProductPermission
from .filters import UserFilterBackend


class MainView(TemplateView):
    template_name = "mainpage.html"


class AboutView(TemplateView):
    template_name = "about.html"


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    queryset = Product.objects.all()
    success_url = 'products'
    context_object_name = 'all_product_list'


class ProductPageView(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        context = {'product': product}
        return render(request, 'product_detail.html', context)


class ProductCreateView(LoginRequiredMixin, CreateView):
    template_name = 'productcreate.html'
    http_method_names = ['get', 'post']
    form_class = ProductForm
    success_url = '/products'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form=form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    template_name = 'productupdate.html'
    form_class = ProductForm
    success_url = '/products'

    def get_initial(self):
        initial = super().get_initial()
        product = self.get_object() 
        initial['name'] = product.name
        initial['text'] = product.text
        initial['price'] = product.price
        initial['count_in_storage'] = product.count_in_storage
        
        return initial
 

class ReturnListView(LoginRequiredMixin, ListView):
    model = Return
    template_name = 'returns.html'
    queryset = Return.objects.all()
    context_object_name = 'all_returns_list'

    def post(self, request):
        purchase_id = request.POST.get('purchase_id')

        purchase = Purchase.objects.get(pk=purchase_id)
        now = datetime.now(timezone.utc)

        if (now - purchase.create_at).total_seconds() > 180:
            messages.error(request, 'Return is no longer possible')
            return redirect('purchases')

        Return.objects.create(
            purchase=purchase
        )
        messages.success(request, 'Return created successfully. Waiting for admin confirmation.')
        return redirect('returns')


class ReturnConfirmView(View):
    def post(self, request, return_id):
        return_obj = Return.objects.get(id=return_id)
        for product in return_obj.purchase.product.all():
            product.count_in_storage = F('count_in_storage') + return_obj.purchase.count
            product.save()
        all_price = return_obj.purchase.count * product.price
        user = return_obj.purchase.user
        user.wallet = F('wallet') + all_price
        user.save()
        return_obj.purchase.delete()
        return_obj.delete()
        return redirect('returns')


class ReturnRejectView(View):
    def post(self, request, return_id):
        return_obj = Return.objects.get(id=return_id)
        return_obj.delete()   
        return redirect('returns')


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'purchases.html'
    context_object_name = 'all_purchases_list'
    success_url = 'purchases'
    
    def get_queryset(self):
        return Purchase.objects.filter(user__user=self.request.user)

    def post(self, request):
        pk = request.POST.get('pk')
        coun = request.POST.get('count')
        product = Product.objects.get(pk=pk)
        user = Client.objects.get(user=request.user)
        if product.count_in_storage < int(coun):
            messages.error(request, 'Not enough products in storage')
            return redirect('purchases')
        total_cost = product.price * int(coun)
        if total_cost > user.wallet:
            messages.error(request, 'You dont have enough money')
            return redirect('purchases')
        purchase = Purchase.objects.create(user=user, count=coun)
        purchase.product.add(product)
        purchase.create_at = datetime.now()
        purchase.save()
        product.count_in_storage = F('count_in_storage') - int(coun)
        product.save()
        user.wallet = F('wallet') - total_cost
        user.save()
        messages.success(request, 'Purchase completed successfully')

        return redirect('purchases')


class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]
    

class PurchaseModelViewSet(ModelViewSet):
    serializer_class = PurchaseSerializer
    permission_classes = [IsAuthenticated]
    queryset = Purchase.objects.all()
    filter_backends = [UserFilterBackend]

    def create(self, request, *args, **kwargs):
        product_id = request.data['product'][0].get('id')
        count = int(request.data.get('count'))
        product = Product.objects.get(pk=product_id)
        user = Client.objects.get(user=request.data['user']['user'])
        if product.count_in_storage < int(count):
            return Response({'error': 'Not enough products in storage'})
        total_cost = product.price * int(count)
        if total_cost > user.wallet:
            return Response({'error': 'You dont have enough money'})
        purchase = Purchase.objects.create(user=user, count=count)
        purchase.product.add(product)
        purchase.created_at = datetime.now()
        purchase.save()
        product.count_in_storage = F('count_in_storage') - int(count)
        product.save()
        user.wallet = F('wallet') - total_cost
        user.save()
        return Response({'message': 'Purchase completed successfully'})


class ReturnModelViewSet(ModelViewSet):
    queryset = Return.objects.all()
    serializer_class = ReturnSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        purchase_id = request.data['purchase'].get('id')
        purchase = Purchase.objects.get(pk=purchase_id)
        now = datetime.now(timezone.utc)
        
        if (now - purchase.create_at).total_seconds() > 180:
            return Response({'detail': 'Return is no longer possible'})

        Return.objects.create(purchase=purchase)

        return Response({'detail': 'Return created successfully. Waiting for admin confirmation.'})

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ClientModelViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer