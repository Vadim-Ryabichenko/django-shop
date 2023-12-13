from .forms import RegistrationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy


class Register(CreateView):
    form_class = RegistrationForm
    template_name = 'register.html'
    success_url = reverse_lazy('register_done')


class RegisterDoneView(TemplateView):
    template_name = "register_done.html"


class LoginDoneView(TemplateView):
    template_name = "login_done.html"


class Login(LoginView):
    success_url = reverse_lazy('login_done')
    template_name = 'login.html'

    def get_success_url(self):
        return self.success_url


class Logout(LoginRequiredMixin, LogoutView):
    template_name = 'logout.html'
    success_url = reverse_lazy('login_page')
