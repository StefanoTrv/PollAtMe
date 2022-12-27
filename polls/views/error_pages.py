from django.shortcuts import render


def error_403(request, exception):
    return render(request, '403.html', {'exception': exception})

def error_404(request, exception):
    return render(request, '404.html', {'exception': exception})

def error_500(request):
    return render(request, '500.html')