from django.http import HttpResponseRedirect
from django.conf import settings

# Create your views here.

def privacy_policy(request):
    return HttpResponseRedirect("https://www.iubenda.com/privacy-policy/12378441")