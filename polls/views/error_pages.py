from django.shortcuts import render


def error_403(request, exception):
    return render(request, 'polls/403.html', {'exception': exception})

def error_404(request, exception):
    return render(request, 'polls/404.html', {'exception': exception})

def error_500(request):
    return render(request, 'polls/500.html')