from .models import Product
from django.views.generic import ListView, TemplateView, View, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .forms import ProductForm
from django.shortcuts import redirect



class MainView(TemplateView):
    template_name = "mainpage.html"


class AboutView(TemplateView):
    template_name = "about.html"


class ProductListView(ListView):
    model = Product
    template_name = 'products.html'
    http_method_names = ['get']
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
 

