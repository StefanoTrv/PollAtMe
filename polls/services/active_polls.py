from typing import Callable

from polls.models import Poll
from django.db.models import Count, Q
from polls.exceptions import PollWithoutAlternativesException
from datetime import datetime, timezone


class ActivePollsService:
    """Service to get all active polls from database"""

    def __init__(self) -> None:
        ids = [
            poll.id
            for poll in Poll.objects.annotate(num_alternatives=Count('alternative')).filter(num_alternatives__gt=0)
            if not poll.is_not_started()
        ]
        self.__polls = Poll.objects.filter(id__in=ids)

    def get_ordered_queryset(self, by_field: str = 'title', asc: bool = False):
        """
        Return active polls as ordered queryset by given field
        Default: descendending order by poll title
        """
        if asc:
            return self.__polls.order_by("-end", by_field)
        else:
            return self.__polls.order_by("-end", f'-{by_field}')


class SearchPollQueryBuilder:

    def __init__(self) -> None:
        self.__status_filter = lambda p: True
        self.__type_filter = lambda p: True
        self.__query_filter: Q = Q()

    def title_filter(self, title: str):
        self.__query_filter = self.__query_filter & Q(title__startswith=title)
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
        action = {
            k: lambda p, label=v: p.get_type() == label  # type: ignore
            for k, v in Poll.PollType.choices
        }

        self.__type_filter = action.get(type, self.__type_filter)
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
        return [
            poll
            for poll in Poll.objects.filter(self.__query_filter)
            if self.__status_filter(poll) and self.__type_filter(poll)
        ]


class SearchPollService:
    def search_by_id(self, id: int) -> Poll:
        poll = Poll.objects.get(id=id)
        if poll.alternative_set.count() == 0:
            raise PollWithoutAlternativesException
        return poll
