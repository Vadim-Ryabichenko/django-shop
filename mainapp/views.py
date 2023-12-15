from .models import Product, Return, Purchase
from accountsapp.models import Client
from django.views.generic import ListView, TemplateView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import ProductForm
from django.shortcuts import redirect
from django.contrib import messages



class MainView(TemplateView):
    template_name = "mainpage.html"


class AboutView(TemplateView):
    template_name = "about.html"


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    extra_context = {'products' : Product.objects.all()}
    queryset = Product.objects.all()
    success_url = 'products'


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
 

class ReturnListView(ListView):
    model = Return
    template_name = 'returns.html'
    queryset = Return.objects.all()
    context_object_name = 'returns'


class ReturnConfirmView(View):
    def post(self, request, return_id):
        return_obj = Return.objects.get(id=return_id)
        return_obj.purchase.delete()
        for product in return_obj.purchase.product.all():
            product.count_in_storage += return_obj.purchase.count
            product.save()
        all_price = return_obj.purchase.count * product.price
        user = return_obj.purchase.user
        user.wallet += all_price
        user.save()
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
    context_object_name = 'purchases'
    success_url = 'purchases'
    
    def get_queryset(self):
        return Purchase.objects.filter(user__user=self.request.user)

    def post(self, request):
        product_id = request.POST.get('pk')
        coun = request.POST.get('count')
        
        product = Product.objects.get(pk=product_id)
        user = Client.objects.get(user=request.user)
        
        if product.count_in_storage < coun:
            messages.error(request, 'Недостаточно товаров на складе')
            return redirect('purchases')
        
        total_cost = product.price * coun
        if total_cost > user.wallet:
            messages.error(request, 'У вас недостаточно денег')
            return redirect('purchases')
        
        purchase = Purchase.objects.create(user=user, count=coun)
        purchase.product.add(product)
        purchase.save()
        
        product.count_in_storage -= coun
        product.save()
        
        user.wallet -= total_cost
        user.save()
        
        messages.success(request, 'Покупка успешно совершена')
        return redirect('purchases')