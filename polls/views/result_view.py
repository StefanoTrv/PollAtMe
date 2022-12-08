from typing import Any, Callable, Optional, Type

from django.db import models
from django.views import View
from django import http
from django.views.generic.list import ListView

from polls.models import Preference, Poll
from polls.services import PollResultsService
from polls.services import MajorityJudgementService
from polls.services import SearchPollService

from django.core.exceptions import ObjectDoesNotExist


class ResultView(View):
    """
    Class view che sceglie quale view mostrare in base al tipo di sondaggio
    scelto nel link.
    """
    POLL_DOES_NOT_EXISTS_MSG = "Il sondaggio ricercato non esiste"

    def dispatch(self, request, *args, **kwargs):
        """
        Questo metodo viene invocato quando viene fatta una richiesta
        HTTP (di qualunque tipo).
        Il dispatching avviene verificando gli attributi della poll
        (non funziona il polimorfismo)
        """
        try:
            poll = SearchPollService().search_by_id(kwargs['id'])
            view = self.__dispatch_view(poll)
            return view(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise http.Http404(self.POLL_DOES_NOT_EXISTS_MSG)
    
    def __dispatch_view(self, poll: Poll) -> Callable:
        if hasattr(poll, 'singlepreferencepoll'):
            return SinglePreferenceListView.as_view()
        elif hasattr(poll, 'majorityopinionpoll'):
            return MajorityJudgementListView.as_view()
        else:
            return ShultzePreferenceListView.as_view()

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
    

class ShultzePreferenceListView(ListView):
    model: type[models.Model] = Preference
    template_name: str = 'result_GM.html' ##qui al limite si deciderà se ritornare tutti la stessa pagina

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ##TODO
        return context
    

class MajorityJudgementListView(ListView):
    
    model: type[models.Model] = Preference
    template_name: str = 'result_GM.html' ##qui al limite si deciderà se ritornare tutti la stessa pagina

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.__poll_results_service = MajorityJudgementService()
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        classifica = self.__poll_results_service.search_by_poll_id(self.kwargs['id']).get_classifica()
        winners = self.__poll_results_service.search_by_poll_id(self.kwargs['id']).get_winners()
        vote_list = self.__poll_results_service.search_by_poll_id(self.kwargs['id']).get_voti_alternativa()

        context['poll_id'] = self.kwargs['id']
        context.update(classifica)
        context.update(winners)
        context.update(vote_list)
        return context