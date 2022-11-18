from polls.models import Poll
from django.db.models import Count
from polls.exceptions import PollWithoutChoicesException

class ActivePollsService:
    """Service for get all active polls from database"""

    def __init__(self) -> None:
        self.__queryset = Poll.objects.annotate(num_choices=Count('choice')).filter(num_choices__gt=0)

    def get_queryset(self, asc: bool = False):
        """Return active polls as queryset"""
        if asc:
            return self.__queryset.order_by('text')
        else:
            return self.__queryset.order_by('-text')

class SearchPollService:
    
    def search_by_id(self, id: int) -> Poll:
        poll = Poll.objects.get(id = id)
        if  poll.choice_set.count() == 0:
            raise PollWithoutChoicesException
        return poll
