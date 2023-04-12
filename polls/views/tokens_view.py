from typing import Any, Optional, Type

from django import http
from django.db.models import Model, QuerySet
from django.views.generic.list import ListView
from django.http import HttpResponse

from polls.models import TokenizedPoll, Token
from polls.services import SearchPollService, TicketGenerator
from polls.services.token_generator import generate_tokens


class TokensView(ListView):
    model: Optional[Type[Model]] = Token
    template_name: str = 'polls/tokens_page.html'

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__tokens: QuerySet[Token] = [] #type: ignore
        self.__poll = SearchPollService().search_by_id(335)
        if not isinstance(self.__poll, TokenizedPoll):
            raise http.Http404('Poll not found')

    def generate(self, request: http.HttpRequest, id: int):
        self.__poll = SearchPollService().search_by_id(self.kwargs['id'])
        if not isinstance(self.__poll, TokenizedPoll):
            raise http.Http404('Poll not found')
        generate_tokens(self.__poll, 1)
    
    def get_queryset(self) -> QuerySet[Token]:
        if not isinstance(self.__poll, TokenizedPoll):
            raise http.Http404('Poll not found')
        generate_tokens(self.__poll, 1)
        return Token.objects.filter(poll = self.__poll)

def download_tokens(request: http.HttpRequest, id: int) -> http.FileResponse:

    poll = SearchPollService().search_by_id(id)

    if not isinstance(poll, TokenizedPoll):
        raise http.Http404('Poll not found')
    
    response = TicketGenerator(
        poll, 
        request.scheme if request.scheme is not None else "", 
        request.get_host()
        ).render()
    return response