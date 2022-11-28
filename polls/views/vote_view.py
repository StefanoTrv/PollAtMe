from typing import Any, Callable, Optional, Type

from django import forms, http
from django.core.exceptions import BadRequest, ObjectDoesNotExist
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView

from polls.exceptions import PollWithoutAlternativesException
from polls.forms import (MajorityPreferenceFormSet,
                         SinglePreferenceForm)
from polls.models import (MajorityOpinionJudgement,
                          MajorityPreference, Poll)
from polls.services import SearchPollService

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
            view = self.__dispatch_view(poll)
            return view(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise http.Http404(self.POLL_DOES_NOT_EXISTS_MSG)
        except PollWithoutAlternativesException:
            raise BadRequest(self.NO_ALTERNATIVES_POLL_MSG)
    
    def __dispatch_view(self, poll: Poll) -> Callable:
        if hasattr(poll, 'singlepreferencepoll'):
            return CreateSinglePreferenceView.as_view()
        elif hasattr(poll, 'majorityopinionpoll'):
            return CreateMajorityPreferenceView.as_view()
        else:
            return CreateShultzePreferenceView.as_view()


class CreateSinglePreferenceView(CreateView):

    form_class: Optional[Type[forms.BaseForm]] = SinglePreferenceForm
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


class CreateMajorityPreferenceView(CreateView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'formset_dummy.html'

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> http.response.HttpResponseBase:
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        self.alternatives = self.poll.alternative_set.all()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context

    def form_valid(self, form: forms.BaseInlineFormSet) -> http.HttpResponse:
        preference = MajorityPreference(poll = self.poll)
        preference.save()

        instance: MajorityOpinionJudgement
        for instance in form.save(commit=False):
            instance.preference = preference
            instance.save()
        
        return render(self.request, 'vote_success.html', {'poll_id': self.poll.id})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.alternatives
        return kwargs

    def get_form_class(self) -> Type:
        num_judges = self.alternatives.count()
        return MajorityPreferenceFormSet.get_formset_class(num_judges)
        


class CreateShultzePreferenceView(View):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
