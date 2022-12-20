from polls.models import Poll, SinglePreferencePoll, MajorityOpinionPoll, Alternative
from django.db.models import Count
from polls.exceptions import PollWithoutAlternativesException
from django.db.models import QuerySet

class ActivePollsService:
    """Service for get all active polls from database"""

    def __init__(self) -> None:
        self.__single_preference_polls = SinglePreferencePoll.objects.annotate(num_alternatives=Count('alternative')).filter(num_alternatives__gt=0)
        self.__majority_opinion_polls = MajorityOpinionPoll.objects.annotate(num_alternatives=Count('alternative')).filter(num_alternatives__gt=0)

    def get_ordered_queryset(self, by_field: str = 'text', asc: bool = False):
        """
        Return active polls as ordered queryset by given field
        Default: descendending order by poll text
        """
        if asc:
            ordered_single_preference_polls = self.__single_preference_polls.order_by(by_field)
            ordered_majority_preference_polls = self.__majority_opinion_polls.order_by(by_field)
        else:
            ordered_single_preference_polls = self.__single_preference_polls.order_by(f'-{by_field}')
            ordered_majority_preference_polls = self.__majority_opinion_polls.order_by(f'-{by_field}')
        
        return [
            ordered_majority_preference_polls,
            ordered_single_preference_polls,
            []
        ]
            
class SearchPollService:
    def search_by_id(self, id: int) -> Poll:
        poll = Poll.objects.get(id = id)
        if  poll.alternative_set.count() == 0:
            raise PollWithoutAlternativesException
        return poll
    
    def get_alternatives_of_a_poll(self, poll: Poll) -> QuerySet[Alternative]:
        return Alternative.objects.filter(poll=poll)
