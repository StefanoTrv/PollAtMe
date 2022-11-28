from typing import Any

from django.db import models
from django.views.generic.list import ListView

from polls.models import Preference
from polls.services import PollResultsService
from polls.services import MajorityJudgementService


class SinglePreferenceListView(ListView):

    model: type[models.Model] = Preference
    template_name: str = 'result.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__poll_results_service = PollResultsService()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = self.__poll_results_service.search_by_poll_id(self.kwargs['id']).as_list()
        context['poll_id'] = self.kwargs['id']
        return context
    

class MajorityJudgementListView(ListView):
    model: type[models.Model] = Preference
    template_name: str = 'result_GM.html' ##qui al limite si deciderà se ritornare tutti la stessa pagina

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__poll_results_service = MajorityJudgementService()
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['result'] = self.__poll_results_service.search_by_poll_id(self.kwargs['id']).get_classifica()
        context['poll_id'] = self.kwargs['id']
        return context