from ast import Dict
from typing import Any, Optional, Type

from django import http
from django.db.models import Model
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from polls.models import TokenizedPoll, Token
from polls.services import SearchPollService, TicketGenerator
from polls.services.token_generator import generate_tokens


class TokensView(LoginRequiredMixin, TemplateView):
    model: Optional[Type[Model]] = Token
    template_name: str = 'polls/tokens_page.html'

    def dispatch(self, request: http.HttpRequest, *args, **kwargs):
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        context['object_list'] = Token.objects.filter(poll = self.poll)
        return context
    

@login_required
def download_tokens(request: http.HttpRequest, id: int) -> http.FileResponse:
    poll = SearchPollService().search_by_id(id)
    if poll.author != request.user:
        raise PermissionDenied('Non hai i permessi per cancellare questo sondaggio')
    else:
        poll = SearchPollService().search_by_id(id)
        print(poll)
        if not isinstance(poll, TokenizedPoll):
            raise http.Http404('Poll not found')
        response = TicketGenerator(
            poll, 
            request.scheme if request.scheme is not None else "", 
            request.get_host()
            ).render()
        return response