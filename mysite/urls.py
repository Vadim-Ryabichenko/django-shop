from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views
from accountsapp.views import RembyAuthToken


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', RembyAuthToken.as_view()),
    path('', include('mainapp.urls')),
    path('accounts/', include('accountsapp.urls')),
]