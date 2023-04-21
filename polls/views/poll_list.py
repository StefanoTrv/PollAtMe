from typing import Any, Optional, Type

from django import http
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Model, QuerySet
from django.shortcuts import render
from django.views.generic import FormView, View
from django.views.generic.list import ListView

from polls.forms import SearchPollForm
from polls.models import Poll
from polls.services import PollsListService


class IndexView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 6
    template_name: str = 'polls/poll_list.html'

    def __init__(self, **kwargs: Any) -> None:
        self.__active_poll_service = PollsListService()
        super().__init__(**kwargs)

    def get_queryset(self) -> QuerySet[Poll]:
        return self.__active_poll_service.get_ordered_queryset(desc = False)


class SearchView(FormView):
    template_name: str = 'polls/search_poll.html'
    form_class = SearchPollForm

    def form_valid(self, form: SearchPollForm) -> http.HttpResponse:
        return render(self.request, 'polls/includes/poll_list.html', {
            'object_list': form.to_query().search()
        })

    def form_invalid(self, form: SearchPollForm) -> http.HttpResponse:
        return render(self.request, 'polls/includes/search_form.html', {
            'form': form
        })

class PersonalPollsView(LoginRequiredMixin, ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 6
    template_name: str = 'polls/personal_polls.html'

    def __init__(self, **kwargs: Any) -> None:
        self.__active_poll_service = PollsListService()
        super().__init__(**kwargs)

    def get_queryset(self) -> QuerySet[Poll]:
        return self.__active_poll_service.get_my_polls(self.request.user)

class ClosePollView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.HttpResponse:
        return http.HttpResponse('ok')
        