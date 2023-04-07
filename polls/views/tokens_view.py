from typing import Any, Optional, Type

from django import http
from django.db.models import Model
from django.views.generic.list import ListView

from polls.models import Poll, TokenizedPoll
from polls.services import SearchPollService, generate_pdf
class TokensView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 6
    template_name: str = 'polls/tokens_page.html'

def download_tokens(request: http.HttpRequest, id: int) -> http.HttpResponse:

    poll = SearchPollService().search_by_id(id)

    if not isinstance(poll, TokenizedPoll):
        raise http.Http404('Poll not found')
    
    response = generate_pdf(poll, request.scheme, request.get_host())
    return response