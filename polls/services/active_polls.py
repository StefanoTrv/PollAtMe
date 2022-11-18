from polls.models import Poll
from django.db.models import QuerySet, Count

class ActivePollsService:
    """Service for get all active polls from database"""

    __queryset: QuerySet[Poll]

    def __init__(self) -> None:
        self.__queryset = Poll.objects.annotate(num_choices=Count('choice')).filter(num_choices__gt=0)

    def get_queryset(self, asc: bool = False):
        """Return active polls as queryset"""
        if asc:
            return self.__queryset.order_by('question_text')
        else:
            return self.__queryset.order_by('-question_text')