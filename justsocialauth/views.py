from allauth.account.views import SignupView, LoginView  # type: ignore
from allauth.decorators import rate_limit  # type: ignore
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.urls import reverse

@method_decorator(rate_limit(action="signup"), name="dispatch")
class SignupWithSocialView(SignupView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('account_login'))

signup = SignupWithSocialView.as_view()

class LoginViewWithMessage(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'auth_message' in self.request.session:
            context['message'] = self.request.session['auth_message']
            del self.request.session['auth_message']
        return context

login = LoginViewWithMessage.as_view()