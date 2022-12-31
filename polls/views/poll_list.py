from typing import Any, Optional, Type

from django import http
from django.db.models import Model, QuerySet
from django.shortcuts import render
from django.views.generic import FormView
from django.views.generic.list import ListView

from polls.forms import SearchPollForm
from polls.models import Poll
from polls.services import ActivePollsService


class IndexView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 6
    template_name: str = 'poll_list.html'
    

    def __init__(self, **kwargs: Any) -> None:
        self.__active_poll_service = ActivePollsService()
        super().__init__(**kwargs)

    def get_queryset(self) -> QuerySet[Poll]:
        return self.__active_poll_service.get_ordered_queryset()

class SearchView(FormView):
    template_name: str = 'search_poll.html'
    form_class = SearchPollForm

    def form_valid(self, form: SearchPollForm) -> http.HttpResponse:
        return render(self.request, 'includes/poll_list.html', {
            'object_list': form.to_query().search()
        })
    
    def form_invalid(self, form: SearchPollForm) -> http.HttpResponse:
        return render(self.request, 'includes/search_form.html', {
            'form': form
        })