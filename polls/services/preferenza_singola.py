from __future__ import annotations
from enum import Enum

from polls.models import SinglePreferencePoll, Alternative, SinglePreference
from django.db.models import QuerySet, Count

class WinnerType(Enum):
    WINNER = 1
    DRAW = 2
    LOSE = 3

class SinglePreferencePollResultsService():
    """
    Classe per il calcolo dei risultati dei sondaggi a preferenza singola
    """

    def set_poll(self, poll: SinglePreferencePoll) -> SinglePreferencePollResultsService:
        """
        Imposta il sondaggio da cui ottenere i risultati
        Torna l'oggetto corrente per utilizzare il method chaining
        Va chiamato per primo

            Parameters:
                poll (SinglePreferencePoll): il sondaggio
            Returns:
                self
        """
        self.__poll = poll
        return self

    def as_list(self, reverse=True) -> list[dict]:
        """
        Ritorna i risultati del sondaggio come lista di dictionary

            Parameters:
                reverse (bool): Se le risposte devono essere ordinare in maniera decrescente o no (default: True)
            Returns:
                lista ordinata in base al valore di count di dictionary con la seguente struttura:
                {
                    'alternative': Testo dell'alternativa,
                    'count': Numero di preferenze,
                    'winner': Se l'alternativa ha la maggioranza relativa delle preferenze (in caso di pareggio tra più opzioni non sono previsti vincitori)
                }
        """
        context = self.__get_results()
        return sorted(context, key=lambda d: d['count'], reverse=reverse)

    # privato, deve costruire gli oggetti da ritornare
    def __get_results(self):
        # prendiamo le preferenze dal database e facciamo l'aggregazione
        preferences: QuerySet[SinglePreference] = SinglePreference.objects.filter(poll=self.__poll).values(
            'alternative').annotate(count=Count('alternative')).order_by('-count')  # preferenze per la scelta
        all_alternatives: QuerySet[Alternative] = Alternative.objects.filter(
            poll=self.__poll)  # tutte le scelte possibili
        context = []

        for alternative_key in all_alternatives.values_list('pk', flat=True):
            count = 0
            # se l'alternativa è stata votata allora aggiorniamo il conto
            # se è stata votata è in preferences
            if alternative_key in preferences.values_list('alternative', flat=True):
                count = preferences.get(alternative=alternative_key)['count']

            text = Alternative.objects.get(id=alternative_key).text
            context.append(
                {'alternative': text, 'count': count, 'winner': 3})

        context = sorted(context, key=lambda d: d['count'], reverse=True)
        if context[0]['count'] > context[1]['count']:
            context[0]['winner'] = 1
        else:
            context[0]['winner'] = 2
            i = 1
            while context[i]['count'] == context[i-1]['count']:
                context[i]['winner'] = 2
                i += 1

        return context
