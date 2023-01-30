from django.shortcuts import render

def error_403(request, exception):
    response = render(request, 'polls/403.html', {'exception': exception})
    response.status_code = 403
    return response

def error_404(request, exception):
    response = render(request, 'polls/404.html', {'exception': exception})
    response.status_code = 404
    return response

def error_500(request):
    response = render(request, 'polls/500.html')
    response.status_code = 500
    return response