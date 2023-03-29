from __future__ import annotations
from abc import ABC, abstractmethod
from polls.models import Poll, AuthenticatedPoll, Mapping, PollOptions
from django.contrib.auth.base_user import AbstractBaseUser

def create_poll_service(user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives):
    if form_options.cleaned_data['authentication_required']:
        return AuthenticatedPollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)
    
    return AnonymousPollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)

class PollFactory(ABC):
    def __save_alternatives(self, formset_alternatives, saved_poll):
        formset_alternatives.save(commit=False)
        for alt in formset_alternatives.new_objects:
            alt.poll = saved_poll
            alt.save()

        for alt in formset_alternatives.changed_objects:
            alt[0].save()

        for alt in formset_alternatives.deleted_objects:
            alt.delete()

    @abstractmethod
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        saved_poll: Poll = form_poll.save(commit=False)
        saved_poll.author = user #type: ignore
        saved_poll.save()

        saved_mapping: Mapping = form_mapping.save(commit=False)
        saved_mapping.poll = saved_poll
        saved_mapping.save()

        saved_options: PollOptions = form_options.save(commit=False)
        saved_options.poll = saved_poll
        saved_options.save()

        self.__save_alternatives(formset_alternatives, saved_poll)
        
        return saved_poll

class AnonymousPollFactory(PollFactory):
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        return super().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)

class AuthenticatedPollFactory(PollFactory):
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        base_poll: Poll = super().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)
        saved_poll = AuthenticatedPoll(poll_ptr = base_poll)
        saved_poll.save_base(raw=True)

        return saved_poll