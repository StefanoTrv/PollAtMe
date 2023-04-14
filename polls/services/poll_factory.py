from __future__ import annotations
from polls.models import Poll, AuthenticatedPoll, Mapping, PollOptions, TokenizedPoll
from django.contrib.auth.base_user import AbstractBaseUser


def create_poll_service(user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives):
    if form_poll.cleaned_data['authentication_type'] == Poll.PollAuthenticationType.AUTHENTICATED:
        return AuthenticatedPollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)

    if form_poll.cleaned_data['authentication_type'] == Poll.PollAuthenticationType.TOKENIZED:
        return TokenizedPollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)

    return PollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)


class PollFactory():
    def __save_alternatives(self, formset_alternatives, saved_poll):
        formset_alternatives.save(commit=False)
        for alt in formset_alternatives.new_objects:
            alt.poll = saved_poll
            alt.save()

        for alt in formset_alternatives.changed_objects:
            alt[0].save()

        for alt in formset_alternatives.deleted_objects:
            alt.delete()

    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        saved_poll: Poll = form_poll.save(commit=False)
        saved_poll.author = user  # type: ignore
        saved_poll.save()

        if hasattr(saved_poll, Poll.AUTH_VOTE_TYPE_FIELDNAME) and saved_poll.authentication_type != Poll.PollAuthenticationType.AUTHENTICATED:
            saved_poll.authenticatedpoll.delete(keep_parents=True)

        if hasattr(saved_poll, Poll.TOKEN_VOTE_TYPE_FIELDNAME) and saved_poll.authentication_type != Poll.PollAuthenticationType.TOKENIZED:
            saved_poll.tokenizedpoll.delete(keep_parents=True)

        saved_mapping: Mapping = form_mapping.save(commit=False)
        saved_mapping.poll = saved_poll
        saved_mapping.save()

        saved_options: PollOptions = form_options.save(commit=False)
        saved_options.poll = saved_poll
        saved_options.save()

        self.__save_alternatives(formset_alternatives, saved_poll)
        return saved_poll


class AuthenticatedPollFactory(PollFactory):
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        base_poll: Poll = super().save_poll(user, form_poll, form_mapping,
                                            form_options, formset_alternatives)
        saved_poll = AuthenticatedPoll(poll_ptr=base_poll)
        saved_poll.save_base(raw=True)

        return saved_poll


class TokenizedPollFactory(PollFactory):
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        base_poll: Poll = super().save_poll(user, form_poll, form_mapping,
                                            form_options, formset_alternatives)
        saved_poll = TokenizedPoll(poll_ptr=base_poll)
        saved_poll.save_base(raw=True)

        return saved_poll
