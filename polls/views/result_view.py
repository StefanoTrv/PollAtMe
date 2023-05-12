from typing import Any

from django import http
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from polls.models import Preference
from polls.services import (MajorityJudgementService, SearchPollService,
                            SinglePreferencePollResultsService)

POLL_DOES_NOT_EXISTS_MSG = "Il sondaggio cercato non esiste"
WRONG_POLL_TYPE_MSG = "Il sondaggio non è a preferenza singola, quindi non sono disponibili risultati di questo tipo."

# se si accede alla pagina dei risultati generica, si viene reindirizzati alla pagina dei risultati del metodo principale
def result_redirect_view(request, id):
    try:
        poll = SearchPollService().search_by_id(id)
        match poll.get_type():
            case "Preferenza singola":
                return redirect(reverse('polls:result_single_preference', args=[id]))
            case "Giudizio maggioritario":
                return redirect(reverse('polls:result_MJ', args=[id]))
            case "Metodo Shultze":
                return redirect(reverse('polls:result_shultze', args=[id]))
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
        if(poll.get_type()!="Preferenza singola"): # 404 se il tipo del sondaggio non è preferenza singola
            raise http.Http404(WRONG_POLL_TYPE_MSG)
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
        context['visibility'] = poll.get_visibility()
        context['authentication_type'] = poll.get_authentication_type()
        context['responses_count']=tot_votes

        return context
    

class ShultzePreferenceResultView(_ResultView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = 'result_GM.html'
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO
        return context
    

class MajorityJudgementResultView(_ResultView):

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.template_name = 'polls/results/result_GM.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        poll = SearchPollService().search_by_id(self.kwargs['id'])
        include_synthetic=True
        if('include_synthetic' in self.kwargs):
            include_synthetic= self.kwargs['include_synthetic']!="realonly"
        result_service = MajorityJudgementService(poll,include_synthetic=include_synthetic)

        classifica = result_service.get_classifica()
        winners = result_service.get_winners()
        vote_list = result_service.get_voti_alternativa()

        context['poll_id'] = self.kwargs['id']
        context.update(classifica)
        context.update(winners)
        context.update(vote_list)
        context['poll'] = poll
        context['visibility'] = poll.get_visibility()
        context['authentication_type'] = poll.get_authentication_type()
        context['responses_count']=result_service.get_numero_numero_preferenze()
        context['include_synthetic']=include_synthetic
        return context