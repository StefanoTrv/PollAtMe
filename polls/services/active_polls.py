from polls.models import Poll
from django.db.models import Count
from polls.exceptions import PollWithoutChoicesException

class ActivePollsService:
    """Service for get all active polls from database"""

    def __init__(self) -> None:
        self.__queryset = Poll.objects.annotate(num_choices=Count('choice')).filter(num_choices__gt=0)

    def get_ordered_queryset(self, by_field: str = 'text', asc: bool = False):
        """
        Return active polls as ordered queryset by given field
        Default: descendending order by poll text
        """
        if asc:
            return self.__queryset.order_by(by_field)
        else:
            return self.__queryset.order_by(f'-{by_field}')
            
class SearchPollService:
    
    def search_by_id(self, id: int) -> Poll:
        poll = Poll.objects.get(id = id)
        if  poll.choice_set.count() == 0:
            raise PollWithoutChoicesException
        return poll
