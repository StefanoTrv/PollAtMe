from typing import Callable

from polls.models import Poll
from django.db.models import Q
from polls.exceptions import PollWithoutAlternativesException
from datetime import datetime, timezone
from django.http import Http404

class ActivePollsService:
    """Service to get all active polls from database"""

    def __init__(self) -> None:
        self.__polls = Poll.objects.filter(id__in=[
            poll.id
            for poll in Poll.objects.all()
            if not poll.is_not_started() and poll.alternative_set.count() > 0
        ])

    def get_ordered_queryset(self, by_field: str = 'title', desc: bool = False):
        """
        Return active polls as ordered list by given field, with active polls before ended polls
        Default: descendending order by poll title
        """
        active_polls = [poll for poll in self.__polls if poll.is_active()]
        ended_polls = [poll for poll in self.__polls if poll.is_ended()]
        return [
            *sorted(active_polls, key=lambda p: getattr(p, by_field), reverse=desc), 
            *sorted(ended_polls, key=lambda p: getattr(p, by_field), reverse=desc)
        ]


class SearchPollQueryBuilder:

    def __init__(self) -> None:
        self.__status_filter = lambda p: True
        self.__query_filter: Q = Q()

    def title_filter(self, title: str):
        self.__query_filter = self.__query_filter & Q(title__icontains=title)
        return self

    def status_filter(self, state: str):
        action: dict[str, Callable[[Poll], bool]] = {
            'NOT_STARTED': lambda p: p.is_not_started(),
            'ACTIVE': lambda p: p.is_active(),
            'ENDED': lambda p: p.is_ended()
        }

        self.__status_filter = action.get(state, self.__status_filter)
        return self

    def type_filter(self, type: int):
        self.__query_filter = self.__query_filter & Q(default_type=type)
        return self

    def start_range_filter(self, start=None, end=None):
        start = datetime.min.replace(
            tzinfo=timezone.utc) if start is None else start
        end = datetime.max.replace(tzinfo=timezone.utc) if end is None else end
        self.__query_filter = self.__query_filter & Q(
            start__range=(start, end))
        return self

    def end_range_filter(self, start=None, end=None):
        start = datetime.min.replace(
            tzinfo=timezone.utc) if start is None else start
        end = datetime.max.replace(tzinfo=timezone.utc) if end is None else end
        self.__query_filter = self.__query_filter & Q(end__range=(start, end))
        return self

    def search(self) -> list[Poll]:
        q = Poll.objects.filter(self.__query_filter)

        l =  [
            poll
            for poll in q
            if self.__status_filter(poll) and poll.alternative_set.count() > 0
        ]

        return l


class SearchPollService:
    def search_by_id(self, id: int) -> Poll:
        try:
            poll = Poll.objects.get(id=id)
            if poll.alternative_set.count() == 0:
                raise PollWithoutAlternativesException
        except Poll.DoesNotExist:
            raise Http404("Il sondaggio ricercato non esiste")
        return poll
