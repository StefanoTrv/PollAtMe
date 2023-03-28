from typing import Any, Optional, Type

from django import forms, http
from django.core.exceptions import PermissionDenied
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic.edit import CreateView

from polls.exceptions import PollWithoutAlternativesException
from polls.forms import MajorityPreferenceFormSet, SinglePreferenceForm
from polls.models import MajorityOpinionJudgement, MajorityPreference, Poll
from polls.models.preference import SinglePreference
from polls.services import SearchPollService

# se si accede alla pagina di voto generica, si viene reindirizzati alla pagina di voto del metodo principale


def vote_redirect_view(request, id):
    poll = SearchPollService().search_by_id(id)
    if poll.default_type == 3:
        return redirect(reverse('polls:vote_single_preference', args=[id]))
    else:
        return redirect(reverse('polls:vote_MJ', args=[id]))


class _VotingView(CreateView):
    """
    Class view (de facto astratta) che incorpora ciò che hanno in comune le diverse pagine di voto
    """
    poll: Poll
    voteType: str
    alternatives: QuerySet

    def dispatch(self, request, *args, **kwargs):
        """
        Questo metodo viene invocato quando viene fatta una richiesta
        HTTP (di qualunque tipo).
        """
        try:
            self.poll = SearchPollService().search_by_id(kwargs['id'])
        except PollWithoutAlternativesException:
            raise http.Http404(
                "Il sondaggio ricercato non ha opzioni di risposta")

        self.alternatives = self.poll.alternative_set.all()
        if not self.poll.is_active():
            raise PermissionDenied('Non è possibile votare questo sondaggio')

        if not (self.poll.get_type() == self.voteType or 'preference_id' in request.session):
            raise PermissionDenied(
                'Il voto con metodi alternativi è concesso solo durante il rivoto')

        syntethic_preference = self.__get_syntethic_preference(
            request.session.get('preference_id'))
        if not (self.poll.get_type() == self.voteType or syntethic_preference.poll == self.poll):
            raise PermissionDenied(
                'Il voto con metodi alternativi è concesso solo durante il rivoto\n(Dettagli dell\'errore: la preferenza sintetica è riferita ad un poll diverso)')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Metodo per l'inserimento delle variabili dalla view al template
        """
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context

    def __get_syntethic_preference(self, id):
        if self.poll.get_type() == self.voteType or id is None:
            return None

        if self.voteType == "Preferenza singola":
            vote_class = SinglePreference

        if self.voteType == "Giudizio maggioritario":
            vote_class = MajorityPreference

        return vote_class.objects.get(id=id)


class VoteSinglePreferenceView(_VotingView):

    form_class: Optional[Type[forms.BaseForm]] = SinglePreferenceForm
    template_name: str = 'polls/vote/vote_SP.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.voteType = "Preferenza singola"

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
        new_preference = form.save()

        if self.poll.get_type() == self.voteType:
            synthetic_preference = MajorityPreference.create_synthetic_preference_from_sp(
                new_preference)
            self.request.session['preference_id'] = synthetic_preference.id
            self.request.session['alternative_sp'] = new_preference.alternative.text

            return render(self.request, 'polls/vote_success.html', {'poll': self.poll, 'revote': True})
        else:
            return render(self.request, 'polls/vote_success.html', {'poll': self.poll})


class VoteMajorityJudgmentView(_VotingView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'polls/vote/vote_GM.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.voteType = "Giudizio maggioritario"

    def form_valid(self, form: forms.BaseInlineFormSet) -> http.HttpResponse:
        preference = MajorityPreference(poll=self.poll)
        preference.save()

        instance: MajorityOpinionJudgement
        for instance in form.save(commit=False):
            instance.preference = preference
            instance.save()

        if self.poll.get_type() == self.voteType:
            return render(self.request, 'polls/vote_success.html', {'poll': self.poll})
        else:
            # cancello la preferenza sintetica
            MajorityPreference.objects.get(
                id=self.request.session['preference_id']).delete()
            del self.request.session['preference_id']

            return render(self.request, 'polls/vote_success.html', {'poll': self.poll})

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
