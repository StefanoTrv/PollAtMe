from typing import Any, Callable, Optional, Type

from django import forms, http
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import CreateView
from django.db.models.query import QuerySet

from polls.exceptions import PollWithoutAlternativesException
from polls.forms import (MajorityPreferenceFormSet,
                         SinglePreferenceForm)
from polls.models import (MajorityOpinionJudgement,
                          MajorityPreference, Poll)
from polls.services import SearchPollService

class VotingView(CreateView):
    """
    Class view che incorpora ciò che hanno in comune le diverse pagine di voto
    """
    poll: Poll
    alternatives: QuerySet

    def dispatch(self, request, *args, **kwargs):
        """
        Questo metodo viene invocato quando viene fatta una richiesta
        HTTP (di qualunque tipo).
        """
        try:
            self.poll = SearchPollService().search_by_id(kwargs['id'])
            self.alternatives = self.poll.alternative_set.all()
            if not self.poll.is_active():
                raise PermissionDenied('Non è possibile votare questo sondaggio')
            return super().dispatch(request, *args, **kwargs)
        except PollWithoutAlternativesException:
            raise http.Http404("Il sondaggio ricercato non ha opzioni di risposta")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Metodo per l'inserimento delle variabili dalla view al template
        """
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context


class VoteSinglePreferenceView(VotingView):

    form_class: Optional[Type[forms.BaseForm]] = SinglePreferenceForm
    template_name: str = 'polls/vote/vote_SP.html'

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inizializzo gli argomenti per il form, in questo caso la poll
        da cui estrarre le opzioni
        """
        kwargs = super().get_form_kwargs()
        kwargs['poll'] = self.poll
        return kwargs

    def form_valid(self, form: forms.BaseModelForm) -> http.HttpResponse:
        form.instance.poll = self.poll
        form.save()
        return render(self.request, 'polls/vote_success.html', {'poll_id': self.poll.id})


class VoteMajorityJudgmentView(VotingView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'polls/vote/vote_GM.html'

    def form_valid(self, form: forms.BaseInlineFormSet) -> http.HttpResponse:
        preference = MajorityPreference(poll = self.poll)
        preference.save()

        instance: MajorityOpinionJudgement
        for instance in form.save(commit=False):
            instance.preference = preference
            instance.save()
        
        return render(self.request, 'polls/vote_success.html', {'poll_id': self.poll.id})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['queryset'] = self.alternatives
        return kwargs

    def get_form_class(self) -> Type:
        num_judges = self.alternatives.count()
        return MajorityPreferenceFormSet.get_formset_class(num_judges)
        


class VoteShultzeView(View):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
