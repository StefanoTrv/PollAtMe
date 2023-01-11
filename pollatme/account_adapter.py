from allauth.account.adapter import DefaultAccountAdapter # type: ignore
from django.urls import reverse
from django import http

class JustSocialLogin(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return False
    
    def get_login_redirect_url(self, request: http.HttpRequest):
        return request.GET.get('next', reverse('polls:index'))
    
    def get_logout_redirect_url(self, request: http.HttpRequest):
        return request.GET.get('next', reverse('polls:index'))