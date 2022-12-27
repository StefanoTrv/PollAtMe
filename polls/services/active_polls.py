from polls.models import Poll
from django.db.models import Count
from polls.exceptions import PollWithoutAlternativesException

class ActivePollsService:
    """Service for get all active polls from database"""

    def __init__(self) -> None:
        ids = [
            poll.id 
            for poll in Poll.objects.annotate(num_alternatives=Count('alternative')).filter(num_alternatives__gt=0) 
                if not poll.is_not_started()
        ]
        self.__polls = Poll.objects.filter(id__in = ids)

    def get_ordered_queryset(self, by_field: str = 'title', asc: bool = False):
        """
        Return active polls as ordered queryset by given field
        Default: descendending order by poll title
        """
        if asc:
            return self.__polls.order_by("-end", by_field)
        else:
            return self.__polls.order_by("-end", f'-{by_field}')
            
class SearchPollService:
    def search_by_id(self, id: int) -> Poll:
        poll = Poll.objects.get(id = id)
        if  poll.alternative_set.count() == 0:
            raise PollWithoutAlternativesException
        return poll
