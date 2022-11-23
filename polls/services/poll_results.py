from __future__ import annotations
from typing import Any

from polls.models import Poll, Alternative, Preference
from django.db.models import QuerySet, Count

class PollResultsService():
    
    def search_by_poll_id(self, poll_id: int) -> PollResultsService:
        self.__poll = Poll.objects.get(id = poll_id)
        return self

    def as_list(self, reverse = True) -> list[Any]:
        context = self.__get_results()
        return sorted(context, key=lambda d: d['count'], reverse=reverse)

    #privato, deve costruire gli oggetti da ritornare
    def __get_results(self):
        #prendiamo le preferenze dal database e facciamo l'aggregazione
        preferences: QuerySet[Preference] = Preference.objects.filter(poll = self.__poll.id).values('alternative').annotate(count = Count('alternative')).order_by('-count') #preferenze per la scelta
        all_alternatives: QuerySet[Alternative]= Alternative.objects.filter(poll = self.__poll.id) #tutte le scelte possibili
        context = []

        for alternative_key in all_alternatives.values_list('pk',flat=True):
            count = 0
            #se l'alternativa è stata votata allora aggiorniamo il conto
            #se è stata votata è in preferences
            if alternative_key in preferences.values_list('alternative', flat=True):
                count = preferences.get(alternative = alternative_key)['count']

            text = Alternative.objects.get(id = alternative_key).text
            context.append({'alternative' : text, 'count' : count})
                 
        return context