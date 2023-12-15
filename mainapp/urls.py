from .views import MainView, AboutView, ProductListView, ProductPageView, ProductCreateView, ProductUpdateView, ReturnListView, ReturnConfirmView, ReturnRejectView, PurchaseListView
from django.urls import path


urlpatterns = [
    path('', MainView.as_view(), name = 'mainpage'),
    path('about/', AboutView.as_view(), name = 'about_shop'),
    path('products/', ProductListView.as_view(), name = 'products'),
    path('product/<int:pk>/', ProductPageView.as_view(), name = 'product_detail'),
    path('product/create/', ProductCreateView.as_view(), name = 'create_product'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name = 'update_product'),
    path('returns/', ReturnListView.as_view(), name = 'returns'),
    path('returns/confirm/<int:return_id>/', ReturnConfirmView.as_view(), name='return_confirm'),
    path('returns/reject/<int:return_id>/', ReturnRejectView.as_view(), name='return_reject'),
    path('purchases/', PurchaseListView.as_view(), name = 'purchases'),
]