from typing import Any, Type, Optional, Callable

from django import forms
from django import http
from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.shortcuts import render

from polls.models import Poll, MajorityPreference, Alternative
from polls.forms import SinglePreferenceForm, MajorityOpinionForm
from polls.services import SearchPollService
from polls.exceptions import PollWithoutAlternativesException
from django.core.exceptions import ObjectDoesNotExist, BadRequest
from django.forms import BaseForm, inlineformset_factory

from django.views import View

def dispatch_view(poll: Poll) -> Callable:
    if hasattr(poll, 'singlepreferencepoll'):
        return CreateSinglePreferenceView.as_view()
    elif hasattr(poll, 'majorityopinionpoll'):
        return CreateMajorityPreferenceView.as_view()
    else:
        return CreateShultzePreferenceView.as_view()

class VotingView(View):
    """
    Class view che sceglie quale view mostrare in base al tipo di sondaggio
    scelto nel link.
    """
    POLL_DOES_NOT_EXISTS_MSG = "Il sondaggio ricercato non esiste"
    NO_ALTERNATIVES_POLL_MSG = "Il sondaggio ricercato non ha opzioni di risposta"

    def dispatch(self, request, *args, **kwargs):
        """
        Questo metodo viene invocato quando viene fatta una richiesta
        HTTP (di qualunque tipo).
        Il dispatching avviene verificando gli attributi della poll
        """
        try:
            poll = SearchPollService().search_by_id(kwargs['id'])
            view = dispatch_view(poll)
            return view(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise http.Http404(self.POLL_DOES_NOT_EXISTS_MSG)
        except PollWithoutAlternativesException:
            raise BadRequest(self.NO_ALTERNATIVES_POLL_MSG)

class CreateSinglePreferenceView(CreateView):

    form_class: Optional[Type[BaseForm]] = SinglePreferenceForm
    template_name: str = 'vote_dummy.html'
    poll: Poll = Poll()

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.response.HttpResponseBase:
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inizializzo gli argomenti per il form, in questo caso la poll
        da cui estrarre le opzioni
        """
        kwargs = super().get_form_kwargs()
        kwargs['poll'] = self.poll
        return kwargs

    def get_context_data(self, **kwargs: Any):
        """
        Metodo per l'inserimento delle variabili dalla view al template
        """
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context

    def form_valid(self, form: forms.BaseModelForm) -> http.HttpResponse:
        form.instance.poll = self.poll
        form.save()
        return render(self.request, 'vote_success.html', {'poll_id': self.poll.id})    

class CreateMajorityPreferenceView(TemplateView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'formset_dummy.html'
    poll: Poll = Poll()

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.response.HttpResponseBase:
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        alternatives = SearchPollService().get_alternatives_of_a_poll(self.poll)
        MajorityPreferenceFormSet = inlineformset_factory(
                Alternative, 
                MajorityPreference.responses.through, 
                form=MajorityOpinionForm, can_delete=False, extra=alternatives.count())
        

        context = super().get_context_data(**kwargs)
        context['formset'] = zip(MajorityPreferenceFormSet(queryset=alternatives), alternatives)
        context['poll'] = self.poll
        return context

class CreateShultzePreferenceView(View):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """