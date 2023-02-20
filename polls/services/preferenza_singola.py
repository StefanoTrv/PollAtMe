from __future__ import annotations

from polls.models import Poll, Alternative, SinglePreference
from django.db.models import QuerySet, Count

class SinglePreferencePollResultsService():
    """
    Classe per il calcolo dei risultati dei sondaggi a preferenza singola
    """

    def set_poll(self, poll: Poll) -> SinglePreferencePollResultsService:
        """
        Imposta il sondaggio da cui ottenere i risultati
        Torna l'oggetto corrente per utilizzare il method chaining
        Va chiamato per primo

            Parameters:
                poll (Poll): il sondaggio
            Returns:
                self
        """
        self.__poll = poll
        return self

    def as_list(self, desc=True,include_synthetic=True) -> list[dict]:
        """
        Ritorna i risultati del sondaggio come lista di dictionary

            Parameters:
                desc (bool): Se le risposte devono essere ordinare in maniera decrescente o no (default: True)
            Returns:
                lista ordinata in base al valore di count di dictionary con la seguente struttura:
                {
                    'text': Testo dell'alternativa,
                    'count': Numero di preferenze,
                    'positition': posizione in classifica (rispetto all'ordine richiesto)
                }
        """
        results_as_dict = dict(sorted(self.__get_results(include_synthetic=include_synthetic).items(), reverse=desc))
        results_as_list = []
        position = 1
        for n_votes, alternatives in results_as_dict.items():
            for alternative in alternatives:
                results_as_list.append({
                    'text': alternative,
                    'count': n_votes,
                    'position': position
                })
            position += len(alternatives)
        
        return results_as_list


    # privato, deve costruire gli oggetti da ritornare
    def __get_results(self,include_synthetic=True):
        # prendiamo le preferenze dal database e facciamo l'aggregazione
        if(include_synthetic):
            preferences: QuerySet[SinglePreference] = SinglePreference.objects.filter(poll=self.__poll).values(
                'alternative').annotate(count=Count('alternative')).order_by('-count')  # preferenze per la scelta
        else:
            preferences: QuerySet[SinglePreference] = SinglePreference.objects.filter(poll=self.__poll).filter(synthetic=False).values(
                'alternative').annotate(count=Count('alternative')).order_by('-count')  # preferenze per la scelta
        
        all_alternatives: QuerySet[Alternative] = Alternative.objects.filter(
            poll=self.__poll)  # tutte le scelte possibili
        
        context: dict[int, list] = {}
        for alternative_key in all_alternatives.values_list('pk', flat=True):
            count = 0
            # se l'alternativa è stata votata allora aggiorniamo il conto
            # se è stata votata è in preferences
            if alternative_key in preferences.values_list('alternative', flat=True):
                count: int = preferences.get(alternative=alternative_key)['count']
            if context.get(count) is None:
                context[count]: list = []

            text = Alternative.objects.get(id=alternative_key).text
            context[count].append(text)

        return context
