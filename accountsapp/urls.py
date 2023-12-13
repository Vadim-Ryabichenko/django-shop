from .views import Login, Register, Logout, RegisterDoneView, LoginDoneView
from django.urls import path


urlpatterns = [
    path('register/', Register.as_view(), name = "register_page"),
    path('login/', Login.as_view(), name = "login_page"),
    path('logout/', Logout.as_view(), name = "logout_page"),
    path('registerdone/', RegisterDoneView.as_view(), name='register_done'),
    path('logindone/', LoginDoneView.as_view(), name='login_done'),
]