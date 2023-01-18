from typing import Any, Callable

from django.db import models
from django import http
from django.views.generic.list import ListView
from django.views.generic import TemplateView

from polls.models import Preference, Poll
from polls.services import SinglePreferencePollResultsService
from polls.services import MajorityJudgementService
from polls.services import SearchPollService

from django.core.exceptions import ObjectDoesNotExist

from django.shortcuts import redirect
from django.urls import reverse

POLL_DOES_NOT_EXISTS_MSG = "Il sondaggio ricercato non esiste"

# se si accede alla pagina dei risultati generica, si viene reindirizzati alla pagina dei risultati del metodo principale
def result_redirect_view(request, id):
    try:
        poll = SearchPollService().search_by_id(id)
        if poll.get_type() == "Preferenza singola":
            return redirect(reverse('polls:result_single_preference', args=[id]))
        else:
            return redirect(reverse('polls:result_MJ', args=[id]))
    except ObjectDoesNotExist:
        raise http.Http404(POLL_DOES_NOT_EXISTS_MSG)

class _ResultView(TemplateView):
    model: type[models.Model] = Preference
    template_name: str = ''
    """
    Class view (de facto astratta) che incorpora ciò che hanno in comune le diverse pagine dei risultati
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Questo metodo viene invocato quando viene fatta una richiesta
        HTTP (di qualunque tipo).
        """
        try:
            SearchPollService().search_by_id(kwargs['id']) #per assicurarsi che il sondaggio esista
            return super().dispatch(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise http.Http404(POLL_DOES_NOT_EXISTS_MSG)

class SinglePreferenceResultView(_ResultView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = 'polls/results/result_SP.html'

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
    

class ShultzePreferenceResultView(_ResultView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = 'result_GM.html'
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO
        return context
    

class MajorityJudgementListView(_ResultView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = 'polls/results/result_GM.html'

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