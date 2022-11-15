from django.views.generic.list import ListView
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.db import models

from polls.models import Vote, Choice


class SinglePreferenceListView(ListView):

    model: type[models.Model] = Vote
    template_name: str = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        votes = self.__getVotes(self.kwargs['id'])
        context["votes"] = votes
        return context

    #privato, deve costruire gli oggetti da ritornare
    def __getVotes(self, question_id):
        #prendiamo i voti dal database e facciamo l'aggregazione
        voti: QuerySet[Vote] = Vote.objects.filter(question = question_id).values("choice").annotate(count = Count('choice')).order_by('-count')
        #creiamo le coppie
        context = []
        for voto in voti:
            choice = voto['choice']
            testoRisposta = Choice.objects.get(id = choice)
            context.append({'choice' : testoRisposta.choice_text, 'count' : voto['count']})
        return context



