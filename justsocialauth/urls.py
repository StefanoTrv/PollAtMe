from importlib import import_module

from allauth import app_settings  # type: ignore
from allauth.account import views  # type: ignore
from allauth.socialaccount import providers  # type: ignore
from django.urls import include, path

from .views import signup

urlpatterns = [
    path("signup/", signup, name="account_signup"),
    path("login/", views.login, name="account_login"),
    path("logout/", views.logout, name="account_logout"),
]

if app_settings.SOCIALACCOUNT_ENABLED:
    urlpatterns += [path("social/", include("allauth.socialaccount.urls"))]

# Provider urlpatterns, as separate attribute (for reusability).
provider_urlpatterns = []
for provider in providers.registry.get_list():
    try:
        prov_mod = import_module(provider.get_package() + ".urls")
    except ImportError:
        continue
    prov_urlpatterns = getattr(prov_mod, "urlpatterns", None)
    if prov_urlpatterns:
        provider_urlpatterns += prov_urlpatterns
urlpatterns += provider_urlpatterns
