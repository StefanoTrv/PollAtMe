from typing import Any

from django.db import models
from django.views.generic.list import ListView

from polls.models import Vote
from polls.services import PollResultsService


class SinglePreferenceListView(ListView):

    model: type[models.Model] = Vote
    template_name: str = 'result.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__poll_results_service = PollResultsService()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = self.__poll_results_service.search_by_poll_id(self.kwargs['id']).as_list()
        context['poll_id'] = self.kwargs['id']
        return context