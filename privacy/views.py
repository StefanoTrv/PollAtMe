from django.http import HttpResponseRedirect
from django.conf import settings

# Create your views here.

def privacy_policy(request):
    return HttpResponseRedirect(f"{settings.STATIC_URL}docs/privacy-policy-12378441.pdf")