from __future__ import annotations

from polls.models import Poll, Alternative, SinglePreference
from django.db.models import QuerySet, Count

class SinglePreferencePollResultsService():
    """
    Class for calculating results of single preference polls
    """

    def set_poll(self, poll: Poll) -> SinglePreferencePollResultsService:
        """
        Set the poll from which we obtain results. 
        It returns the current object to use with chaining method
        It must be called as first

            Parameters:
                poll (Poll): the poll
            Returns:
                self
        """
        self.__poll = poll
        return self

    def as_list(self, desc=True,include_synthetic=True) -> list[dict]:
        """
        Returns poll results as list of dictionary

            Parameters:
                desc (bool): If responses must be ordered in an ascendant or descendant way (default: True)
            Returns:
                ordered list based on count value of dictionary, having the following structure:
                {
                    'text': alternative text,
                    'count': number of preferences,
                    'positition': ranking order (with regard to required order)
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

    # private, it must build the objects which are returned
    def __get_results(self,include_synthetic=True):
        # we take preferences from database e we aggregate them
        if(include_synthetic):
            preferences: QuerySet[SinglePreference] = SinglePreference.objects.filter(poll=self.__poll).values(
                'alternative').annotate(count=Count('alternative')).order_by('-count')  # poll preferences
        else:
            preferences: QuerySet[SinglePreference] = SinglePreference.objects.filter(poll=self.__poll).filter(synthetic=False).values(
                'alternative').annotate(count=Count('alternative')).order_by('-count')  # poll preferences 
        
        all_alternatives: QuerySet[Alternative] = Alternative.objects.filter(
            poll=self.__poll)  # all possible choices
        
        context: dict[int, list] = {}
        for alternative_key in all_alternatives.values_list('pk', flat=True):
            count = 0
            # if alternative has been voted we then updated the count
            # if was voted, it is in preferences
            if alternative_key in preferences.values_list('alternative', flat=True):
                count: int = preferences.get(alternative=alternative_key)['count']
            if context.get(count) is None:
                context[count]: list = []

            text = Alternative.objects.get(id=alternative_key).text
            context[count].append(text)

        return context
