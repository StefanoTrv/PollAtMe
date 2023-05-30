from __future__ import annotations
from polls.models import Poll, AuthenticatedPoll, Mapping, PollOptions, TokenizedPoll
from django.contrib.auth.base_user import AbstractBaseUser

"""
    Creates and saves a poll based on the authentication type specified in the form.

    Args:
        user: The user associated with the poll.
        form_poll: Form data for the poll.
        form_mapping: Form data for the mapping (the shortened urls).
        form_options: Form data for the poll options.
        formset_alternatives: Formset data for the alternatives.

    Returns:
        The created poll object.
    """
def create_poll_service(user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives):
    if form_poll.cleaned_data['authentication_type'] == Poll.PollAuthenticationType.AUTHENTICATED:
        return AuthenticatedPollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)

    if form_poll.cleaned_data['authentication_type'] == Poll.PollAuthenticationType.TOKENIZED:
        return TokenizedPollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)

    return PollFactory().save_poll(user, form_poll, form_mapping, form_options, formset_alternatives)


"""
Factory class for creating a generic Poll object.
"""
class PollFactory():


    """
    Save the alternatives related to the poll.

    Args:
        formset_alternatives: Formset data for the alternatives.
        saved_poll: The saved poll object.
    """
    def __save_alternatives(self, formset_alternatives, saved_poll):
        formset_alternatives.save(commit=False)
        for alt in formset_alternatives.new_objects:
            alt.poll = saved_poll
            alt.save()

        for alt in formset_alternatives.changed_objects:
            alt[0].save()

        for alt in formset_alternatives.deleted_objects:
            alt.delete()


    """
    Save the poll object.

    Args:
        user: The user associated with the poll.
        form_poll: Form data for the poll.
        form_mapping: Form data for the mapping (the shortened urls).
        form_options: Form data for the poll options.
        formset_alternatives: Formset data for the alternatives.

    Returns:
        The saved poll object.
    """
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


"""
Factory class for creating AuthenticatedPoll objects.
"""
class AuthenticatedPollFactory(PollFactory):

    """
    Save the AuthenticatedPoll object.

    Args:
        user: The user associated with the poll.
        form_poll: Form data for the poll.
        form_mapping: Form data for the mapping (the shortened urls).
        form_options: Form data for the poll options.
        formset_alternatives: Formset data for the alternatives.

    Returns:
        The saved AuthenticatedPoll object.
    """
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        base_poll: Poll = super().save_poll(user, form_poll, form_mapping,
                                            form_options, formset_alternatives)
        saved_poll = AuthenticatedPoll(poll_ptr=base_poll)
        saved_poll.save_base(raw=True)

        return AuthenticatedPoll.objects.get(pk=base_poll.pk)


"""
Factory class for creating TokenizedPoll objects.
"""
class TokenizedPollFactory(PollFactory):

    """
    Save the TokenizedPoll object.

    Args:
        user: The user associated with the poll.
        form_poll: Form data for the poll.
        form_mapping: Form data for the mapping (the shortened urls).
        form_options: Form data for the poll options.
        formset_alternatives: Formset data for the alternatives.

    Returns:
        The saved TokenizedPoll object.
    """
    def save_poll(self, user: AbstractBaseUser, form_poll, form_mapping, form_options, formset_alternatives) -> Poll:
        base_poll: Poll = super().save_poll(user, form_poll, form_mapping,
                                            form_options, formset_alternatives)
        saved_poll = TokenizedPoll(poll_ptr=base_poll)
        saved_poll.save_base(raw=True)

        return TokenizedPoll.objects.get(pk=base_poll.pk)
