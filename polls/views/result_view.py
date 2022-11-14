from typing import *


from django.http import HttpRequest, HttpResponse
from django.db.models import Count
from django.shortcuts import render


from polls.models import Vote, Choice, Question

#quick and dirty
def displayResult(request, *args, **kwargs) -> HttpResponse:
    #dobbiamo andare a prendere la risposta
    voti = Vote.objects.filter(question__exact = kwargs["id"]).values('choice').annotate(count = Count('choice')).order_by('-count')
    return render(request, "result.html", {'risultati' : voti})



