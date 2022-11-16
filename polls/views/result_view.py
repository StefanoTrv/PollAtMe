from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet
from django.views.generic.list import ListView

from polls.models import Choice, Vote


class SinglePreferenceListView(ListView):

    model: type[models.Model] = Vote
    template_name: str = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["votes"] = self.__getVotes(self.kwargs['id'])
        return context

    #privato, deve costruire gli oggetti da ritornare
    def __getVotes(self, question_id):
        #prendiamo i voti dal database e facciamo l'aggregazione
        voti: QuerySet[Vote] = Vote.objects.filter(question = question_id).values("choice").annotate(count = Count('choice')).order_by('-count') #voti per la scelta
        all_choices: QuerySet[Choice]= Choice.objects.filter(question = question_id) #tutte le scelte possibili
        context = []

        for choice_key in all_choices.values_list('pk',flat=True):
            count = 0
            #se la scelta è stata votata allora aggiorniamo il conto
            #se è stata votata è in voti
            if choice_key in voti.values_list('choice', flat=True):
                count = voti.get(choice = choice_key)['count']

            text = Choice.objects.get(id = choice_key) # all_choices.get(choiceKey)['choice_text']
            text = text.choice_text
            context.append({'choice' : text, 'count' : count})
                 
        return sorted(context, key=lambda d: d['count'], reverse=True)