from typing import Any
from polls.models import Poll, Choice, Vote
from django.db.models import QuerySet, Count, Model

class PollResultsService():
    def __init__(self, poll_id) -> None:
        self.__poll = Poll.objects.get(id = poll_id)
    
    def as_list(self, reverse = True) -> list[Any]:
        context = self.__get_results()
        return sorted(context, key=lambda d: d['count'], reverse=reverse)

    #privato, deve costruire gli oggetti da ritornare
    def __get_results(self):
        #prendiamo i voti dal database e facciamo l'aggregazione
        voti: QuerySet[Vote] = Vote.objects.filter(poll = self.__poll.id).values('choice').annotate(count = Count('choice')).order_by('-count') #voti per la scelta
        all_choices: QuerySet[Choice]= Choice.objects.filter(poll = self.__poll.id) #tutte le scelte possibili
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
                 
        return context