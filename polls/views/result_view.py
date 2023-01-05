from typing import Any, Callable

from django.db import models
from django.views import View
from django import http
from django.views.generic.list import ListView
from django.views.generic import TemplateView

from polls.models import Preference, Poll
from polls.services import SinglePreferencePollResultsService
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
        """
        try:
            poll = SearchPollService().search_by_id(kwargs['id'])
            view = self.__dispatch_view(poll)
            return view(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise http.Http404(self.POLL_DOES_NOT_EXISTS_MSG)
    
    def __dispatch_view(self, poll: Poll) -> Callable:
        if poll.get_type() == 'Preferenza singola':
            return SinglePreferenceListView.as_view()
        elif poll.get_type() == 'Giudizio maggioritario':
            return MajorityJudgementListView.as_view()
        else:
            return ShultzePreferenceListView.as_view()

class SinglePreferenceListView(TemplateView):

    model: type[models.Model] = Preference
    template_name: str = 'results/result_SP.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poll = SearchPollService().search_by_id(self.kwargs['id'])
        results = SinglePreferencePollResultsService().set_poll(poll).as_list()

        tot_votes = sum([votes['count'] for votes in results])
        for res in results:
            if tot_votes == 0:
                res['percentage'] = '0.00'
            else:
                res['percentage'] = "%.2f" % ((res['count']/tot_votes)*100)
        
        context['results'] = results
        context['unique_winner'] = results[0]['position'] != results[1]['position']
        context['poll'] = poll

        return context
    
    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> http.HttpResponse:
        return super().render_to_response(context, **response_kwargs)
    

class ShultzePreferenceListView(TemplateView):
    model: type[models.Model] = Preference
    template_name: str = 'result_GM.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO
        return context
    

class MajorityJudgementListView(TemplateView):
    
    model: type[models.Model] = Preference
    template_name: str = 'results/result_GM.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        poll = SearchPollService().search_by_id(self.kwargs['id'])
        result_service = MajorityJudgementService(poll)

        classifica = result_service.get_classifica()
        winners = result_service.get_winners()
        vote_list = result_service.get_voti_alternativa()

        context['poll_id'] = self.kwargs['id']
        context.update(classifica)
        context.update(winners)
        context.update(vote_list)
        context['poll'] = poll
        return context