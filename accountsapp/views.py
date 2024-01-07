from .forms import RegistrationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


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


class RembyAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'attention': f'{user.username}, this is now your new token',
            'token': token.key,
            'user_id': user.pk,
            'user_first_name': user.first_name,
            'user_last_name': user.last_name,
        })
