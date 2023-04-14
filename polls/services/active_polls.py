from typing import Callable

from polls.models import Poll
from django.db.models import Q
from polls.exceptions import PollWithoutAlternativesException
from datetime import datetime, timezone
from django.http import Http404
from django.utils import timezone as tz


class PollsListService:
    """Service to get all active polls from database"""

    def __init__(self) -> None:
        self.__polls = Poll.objects.filter(id__in=[
            poll.id
            for poll in Poll.objects.all()
            if poll.alternative_set.count() > 0
        ])

    def get_my_polls(self, author, by_field: str = 'last_update', desc: bool = True):

        return self.__polls.filter(author = author).order_by(by_field if not desc else f'-{by_field}')


    def get_ordered_queryset(self, desc: bool = False, include_hidden: bool = False):
        """
        Return active polls as ordered list by given field, with active polls before ended polls
        Default: descendending order by time
                 hidden polls are not included
        """

        active_polls = [poll for poll in self.__polls if (poll.is_active() and (poll.is_public() or include_hidden))]
        ended_polls = [poll for poll in self.__polls if (poll.is_ended() and (poll.is_public() or include_hidden))]
        return [
            *sorted(active_polls, key=lambda p: getattr(p, 'end') - tz.now(), reverse = desc), 
            *sorted(ended_polls, key=lambda p: getattr(p, 'end') - tz.now(), reverse = not desc)
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

    def public_filter(self, only_public = True):
        if only_public:
            self.__query_filter = self.__query_filter & Q(visibility=Poll.PollVisibility.PUBLIC)


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
        
        if hasattr(poll, Poll.AUTH_VOTE_TYPE_FIELDNAME):
            poll = getattr(poll, Poll.AUTH_VOTE_TYPE_FIELDNAME)

        if hasattr(poll, Poll.TOKEN_VOTE_TYPE_FIELDNAME):
            poll = getattr(poll, Poll.TOKEN_VOTE_TYPE_FIELDNAME)
            
        return poll
