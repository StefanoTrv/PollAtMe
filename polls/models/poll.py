from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .token import Token

User = get_user_model()

class Poll(models.Model):
    class PollType(models.IntegerChoices):
        MAJORITY_JUDGMENT = 1, _("Giudizio maggioritario")
        #SHULTZE_METHOD = 2, _("Metodo Shultze")
        SINGLE_PREFERENCE = 3, _("Preferenza singola")

    class PollVisibility(models.IntegerChoices):
        PUBLIC = 1, _("Pubblico")
        HIDDEN = 2, _("Nascosto")

    class PollAuthenticationType(models.IntegerChoices):
        FREE = 1, _("Libero")
        AUTHENTICATED = 2, _("Solo autenticati")
        TOKENIZED = 3, _("Solo con password")

    class PollResultsRestriction(models.IntegerChoices):
        ALL = 1, _("Libero")
        AUTHOR = 2, _("Solo creatore")
        NOBODY = 3, _("Nessuno")

    title = models.CharField(max_length=100)
    text = models.TextField(default="")
    default_type = models.IntegerField(choices=PollType.choices, default=PollType.MAJORITY_JUDGMENT)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    start = models.DateTimeField(auto_now_add = False, auto_now = False)
    end = models.DateTimeField(auto_now_add = False, auto_now = False)

    creation_date = models.DateTimeField(auto_now_add = True)
    last_update = models.DateTimeField(auto_now = True)

    visibility = models.IntegerField(choices=PollVisibility.choices, default=PollVisibility.HIDDEN)

    AUTH_VOTE_TYPE_FIELDNAME = 'authenticatedpoll'
    TOKEN_VOTE_TYPE_FIELDNAME = 'tokenizedpoll'
    authentication_type = models.IntegerField(choices=PollAuthenticationType.choices, default=PollAuthenticationType.FREE)

    results_restriction = models.IntegerField(choices=PollResultsRestriction.choices, default=PollResultsRestriction.ALL)

    MAPPING_FIELDNAME = 'mapping'
    OPTIONS_FIELDNAME = 'polloptions'

    def is_active(self) -> bool:
        return self.start <= timezone.now() < self.end

    def is_ended(self) -> bool:
        return timezone.now() >= self.end
    
    def is_not_started(self) -> bool:
        return timezone.now() < self.start

    def get_type(self) -> str:
        return self.PollType(self.default_type).label
    
    def get_visibility(self) -> str:
        return self.PollVisibility(self.visibility).label
    
    def get_authentication_type(self) -> str:
        return self.PollAuthenticationType(self.authentication_type).label
    
    def is_public(self) -> bool:
        return self.visibility == Poll.PollVisibility.PUBLIC
    
    def failed_authentication(self, **kwargs) -> bool:
        return False
    
    def user_has_already_voted(self, **kwargs) -> bool:
        return False
    
    def set_authentication_method_as_used(self, **kwargs) -> None:
        pass
    
    def __str__(self) -> str:
        return self.title

class PollOptions(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE)

    random_order = models.BooleanField(default=True)

class AuthenticatedPoll(Poll):
    users_that_have_voted = models.ManyToManyField(User)

    def clean(self) -> None:
        if self.poll.authentication_type != Poll.PollAuthenticationType.AUTHENTICATED : # type: ignore
            raise ValidationError(_("AuthenticatedPoll is only for authenticated polls"))
    
    def failed_authentication(self, **kwargs) -> bool:
        return not kwargs.get('user', False)

    def user_has_already_voted(self, **kwargs) -> bool:
        return self.users_that_have_voted.filter(pk=kwargs['user'].pk).exists()

    def set_authentication_method_as_used(self, **kwargs) -> None:
        if not self.user_has_already_voted(user=kwargs["user"]):
            self.users_that_have_voted.add(kwargs['user'])
        else:
            raise ValidationError(_("User has already voted"))

class TokenizedPoll(Poll):
    def clean(self) -> None:
        if self.poll.authentication_type != Poll.PollAuthenticationType.TOKENIZED : # type: ignore
            raise ValidationError(_("TokenizedPoll is only for polls with tokens"))
    
    def failed_authentication(self, **kwargs) -> bool:
        return not Token.objects.filter(poll=self,token=kwargs['token'].lower()).exists()

    def user_has_already_voted(self, **kwargs) -> bool:
        return Token.objects.get(token=kwargs['token'].lower(),poll=self).used

    def set_authentication_method_as_used(self, **kwargs) -> None:
        if self.failed_authentication(**kwargs):
            raise ValidationError(_("The token is not valid"))
        elif self.user_has_already_voted(**kwargs):
            raise ValidationError(_("The token was already used"))
        else:
            token_object = Token.objects.get(token=kwargs['token'].lower(),poll=self)
            token_object.used = True
            token_object.save()