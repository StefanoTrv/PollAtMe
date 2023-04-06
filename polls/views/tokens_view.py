from typing import Any, Optional, Type

from django import http
from django.db.models import Model, QuerySet
from django.shortcuts import render
from django.views.generic.list import ListView

from polls.models import Poll

class TokensView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 6
    template_name: str = 'polls/tokens_page.html'