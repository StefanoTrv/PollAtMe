from allauth.account.views import SignupView  # type: ignore
from allauth.decorators import rate_limit  # type: ignore
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse


@method_decorator(rate_limit(action="signup"), name="dispatch")
class SignupWithSocialView(SignupView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('account_login'))

signup = SignupWithSocialView.as_view()