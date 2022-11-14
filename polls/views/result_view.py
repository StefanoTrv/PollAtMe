from typing import *


from django.http import HttpRequest, HttpResponse
from django.db.models import Count
from django.shortcuts import render
from django.db.models.query import QuerySet

from polls.models import Vote, Choice, Question

#quick and dirty
def displayResult(request, *args, **kwargs) -> HttpResponse:
    #dobbiamo andare a prendere la risposta
    voti: QuerySet[Vote] = Vote.objects.filter(question = kwargs["id"])
    count = voti.values('choice').annotate(count = Count('choice')).order_by('-count')
    return render(request, "result.html", {'risultati' : voti, 'count': count})



