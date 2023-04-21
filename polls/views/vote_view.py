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
from polls.models import MajorityPreference, Poll
from polls.models.preference import SinglePreference
from polls.services import SearchPollService
from polls.services import check
from django.contrib.auth.views import redirect_to_login


# se si accede alla pagina di voto generica, si viene reindirizzati alla pagina di voto del metodo principale


def vote_redirect_view(request, id, token=None):
    poll = SearchPollService().search_by_id(id)
    if token is None:
        args = [id]
    else:
        args = [id, token]

    if poll.default_type == Poll.PollType.SINGLE_PREFERENCE:
        return redirect(reverse('polls:vote_single_preference', args=args))

    if poll.default_type == Poll.PollType.MAJORITY_JUDGMENT:
        return redirect(reverse('polls:vote_MJ', args=args))


class _VoteView(CreateView):
    """
    Class view (de facto astratta) che incorpora ciò che hanno in comune le diverse pagine di voto
    """
    poll: Poll
    pollType: str
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
        syntethic_preference = self.__get_syntethic_preference(
            request.session.get('preference_id', None))
        self.alternatives = self.poll.alternative_set.all()
        self.token = kwargs.get('token', '').replace('-', ' ')

        check_activeness = check.CheckPollActiveness(self.poll)
        check_authentication = check.CheckAuthentication(self.poll, request.user.is_authenticated, self.token, self.__failed_authentication)
        check_already_voted = check.CheckUserHasVoted(self.poll, request.user, self.token, syntethic_preference, 
                                                      lambda: render(self.request, 'polls/already_voted.html', {'poll': self.poll}))
        check_revote = check.CheckRevoteSession(self.poll, self.pollType, 'preference_id' in request.session, syntethic_preference)

        check_activeness.set_next(check_authentication).set_next(check_already_voted).set_next(check_revote)
        passed = check_activeness.handle()

        return passed if passed else super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Metodo per l'inserimento delle variabili dalla view al template
        """
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        return context

    def __get_syntethic_preference(self, id):
        if id is None or self.poll.get_type() == self.pollType:
            return None

        if self.pollType == "Preferenza singola":
            vote_class = SinglePreference

        if self.pollType == "Giudizio maggioritario":
            vote_class = MajorityPreference

        return vote_class.objects.get(id=id)

    def __failed_authentication(self):
        if self.poll.authentication_type == Poll.PollAuthenticationType.AUTHENTICATED:
            self.request.session['auth_message'] = 'Devi aver effettuato il login per poter votare questa scelta'
            return redirect_to_login(self.request.get_full_path())

        if self.poll.authentication_type == Poll.PollAuthenticationType.TOKENIZED:
            return render(self.request, 'polls/token_request.html', {'poll': self.poll, 'token': self.token})


class VoteSinglePreferenceView(_VoteView):

    form_class: Optional[Type[forms.BaseForm]] = SinglePreferenceForm
    template_name: str = 'polls/vote/vote_SP.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pollType = Poll.PollType.SINGLE_PREFERENCE.label

    def get_form_kwargs(self) -> dict[str, Any]:
        """
        Inizializzo gli argomenti per il form, in questo caso la poll
        da cui estrarre le opzioni
        """
        kwargs = super().get_form_kwargs()
        kwargs['poll'] = self.poll
        return kwargs

    def form_valid(self, form: forms.BaseModelForm) -> http.HttpResponse:
        self.poll.set_authentication_method_as_used(
            user=self.request.user, token=self.token)

        form.instance.poll = self.poll
        new_preference = form.save()

        if self.poll.get_type() == self.pollType:
            synthetic_preference = MajorityPreference.save_mj_from_sp(
                new_preference)
            self.request.session['preference_id'] = synthetic_preference.id
            self.request.session['alternative_sp'] = new_preference.alternative.text
            return render(self.request, 'polls/vote_success.html', {'poll': self.poll, 'revote': True, 'token': self.token})

        return render(self.request, 'polls/vote_success.html', {'poll': self.poll})


class VoteMajorityJudgmentView(_VoteView):
    """
    Class view per l'inserimento delle risposte ai sondaggi a risposta singola
    """
    template_name: str = 'polls/vote/vote_GM.html'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.pollType = Poll.PollType.MAJORITY_JUDGMENT.label

    def form_valid(self, form: forms.BaseInlineFormSet) -> http.HttpResponse:
        synthetic_id = self.request.session.pop('preference_id', False)
        if not synthetic_id:
            self.poll.set_authentication_method_as_used(
                user=self.request.user, token=self.token)

        if synthetic_id:
            preference = MajorityPreference.objects.get(id=synthetic_id)
        else:
            preference = MajorityPreference()
            preference.poll = self.poll

        preference.synthetic = False
        preference.save()
        preference.save_mj_judgements(form.save(commit=False))

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
    Class view per l'inserimento delle risposte ai sondaggi con metodo Shultze
    """
