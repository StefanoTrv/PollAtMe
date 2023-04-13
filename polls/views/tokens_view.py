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

    def dispatch(self, request, *args, **kwargs):
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        if self.poll.author != request.user:
            raise PermissionDenied('Non è possibile accedere a questa pagina')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        context['all_tokens'] = Token.objects.filter(poll = self.poll).count
        context['tokens_used'] = Token.objects.filter(poll = self.poll, used=True).count
        context['tokens_available'] = Token.objects.filter(poll = self.poll, used=False).count
        return context
    
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        number_of_tokens = self.request.POST.get("n")
        context['poll'] = self.poll
        generate_token(request, self.poll, int(number_of_tokens))
        context['all_tokens'] = Token.objects.filter(poll = self.poll).count
        context['tokens_used'] = Token.objects.filter(poll = self.poll, used=True).count
        context['tokens_available'] = Token.objects.filter(poll = self.poll, used=False).count
        return render(self.request, 'polls/tokens_page.html', context)


@login_required
def generate_token(request: http.HttpRequest, poll: TokenizedPoll, number_of_tokens: int):
    if not isinstance(poll, TokenizedPoll):
        raise http.Http404('Poll not found')
    generate_tokens(poll, number_of_tokens) 


@login_required
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