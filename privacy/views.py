from django.shortcuts import render

# Create your views here.

def privacy_policy(request):
    return render(request, 'cookiebanner/privacy_policy.html')