from typing import Optional

from django.http import HttpRequest
from django.views.generic import TemplateView
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet

from polls.models import Poll
from polls.forms import PollFormAdditionalOptions, PollFormMain, BaseAlternativeFormSet

ALTERNATIVE_FORMSET = BaseAlternativeFormSet.get_formset_class()

def select_action(request: HttpRequest, poll=None):
    action = 'create' if poll is None else 'edit'
    queryset_alternatives = Poll.objects.none(
    ) if poll is None else poll.alternative_set.all()

    if 'summary' in request.POST:
        return summary(request, action, queryset_alternatives, poll)

    if 'go_back' in request.POST:
        return go_back(request, action, queryset_alternatives, poll)

    if 'save' in request.POST:
        return save(request, action, queryset_alternatives, poll)


def summary(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[Poll] = None):
    form = PollFormMain(request.POST, instance=poll)
    formset_alternatives: BaseAlternativeFormSet = ALTERNATIVE_FORMSET(request.POST, queryset=alternatives)

    if form.is_valid() and formset_alternatives.is_valid():
        poll = form.save(commit=False)
        request.session[action] = {
            'poll': form.cleaned_data,
            'alternatives': formset_alternatives.get_form_for_session()
        }
        return render(request, f'create_poll/summary_and_options_{action}.html', {
            'alternatives': formset_alternatives.get_alternatives_text_list(),
            'form': PollFormAdditionalOptions(instance=poll)
        })
    else:
        return render(request, f'create_poll/main_page_{action}.html', {
            'form': form,
            'formset': formset_alternatives,
        })


def go_back(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[Poll] = None):
    return render(request, f'create_poll/main_page_{action}.html', {
        'form': PollFormMain(request.session[action]['poll'], instance=poll),
        'formset':ALTERNATIVE_FORMSET(request.session[action]['alternatives'], queryset=alternatives)
    })


def save(request: HttpRequest, action: str, alternatives: QuerySet, poll: Optional[Poll] = None):
    form = PollFormAdditionalOptions(request.POST, instance=poll)
    formset_alternatives: BaseAlternativeFormSet = ALTERNATIVE_FORMSET(request.session[action]['alternatives'], queryset=alternatives)

    if form.is_valid() and formset_alternatives.is_valid():
        form.save()
        formset_alternatives.save()
        return render(request, 'create_poll_success.html')
    else:
        render(request, f'create_poll/summary_and_options_{action}.html', {
        'form': PollFormAdditionalOptions(instance=poll),
        'alternatives': formset_alternatives.get_alternatives_text_list()
    })


class CreatePollView(TemplateView):

    def get(self, request: HttpRequest, *args, **kwargs):
        return render(request, 'create_poll/main_page_create.html', {
            'form': PollFormMain(),
            'formset': BaseAlternativeFormSet.get_formset_class()(queryset=Poll.objects.none())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        return select_action(request)


class EditPollView(TemplateView):

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.__poll: Poll = get_object_or_404(Poll, id=kwargs['id'])

        if self.__poll.is_active():
            raise PermissionDenied(
                "Non è possibile modificare il sondaggio perché è in corso la votazione")

        if self.__poll.is_ended():
            raise PermissionDenied(
                "Questo sondaggio è concluso e non può essere modificato")

        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):

        return render(request, 'create_poll/main_page_edit.html', {
            'form': PollFormMain(instance=self.__poll),
            'formset': BaseAlternativeFormSet.get_formset_class()(queryset=self.__poll.alternative_set.all())
        })

    def post(self, request: HttpRequest, *args, **kwargs):
        return select_action(request, self.__poll)
