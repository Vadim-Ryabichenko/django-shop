from datetime import timedelta, datetime
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token



class RembyTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        time_now = (datetime.now() - timedelta(minutes = 10)).replace(tzinfo=None)
        if token.created.replace(tzinfo=None) < time_now:
            token.delete()
            raise exceptions.AuthenticationFailed("Your token has expired")
        return user, token