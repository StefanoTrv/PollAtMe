from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class Poll(models.Model):
    class PollType(models.IntegerChoices):
        MAJORITY_JUDGMENT = 1, _("Giudizio maggioritario")
        #SHULTZE_METHOD = 2, _("Metodo Shultze")
        SINGLE_PREFERENCE = 3, _("Preferenza singola")

    class PollVisibility(models.IntegerChoices):
        PUBLIC = 1, _("Pubblico")
        HIDDEN = 2, _("Nascosto")

    title = models.CharField(max_length=100)
    text = models.TextField(default="")
    default_type = models.IntegerField(choices=PollType.choices, default=PollType.MAJORITY_JUDGMENT)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    start = models.DateTimeField(auto_now_add = False, auto_now = False)
    end = models.DateTimeField(auto_now_add = False, auto_now = False)

    creation_date = models.DateTimeField(auto_now_add = True)
    last_update = models.DateTimeField(auto_now = True)

    visibility = models.IntegerField(choices=PollVisibility.choices, default=PollVisibility.HIDDEN)

    def is_active(self) -> bool:
        return self.start <= timezone.now() < self.end

    def is_ended(self) -> bool:
        return timezone.now() >= self.end
    
    def is_not_started(self) -> bool:
        return timezone.now() < self.start

    def get_type(self) -> str:
        return self.PollType(self.default_type).label
    
    def is_public(self) -> bool:
        return self.visibility == Poll.PollVisibility.PUBLIC
    
    def require_authentication(self, is_auth) -> bool:
        return False
    
    def has_already_voted(self, user) -> bool:
        return False
    
    def add_vote(self, user) -> None:
        pass
    
    def __str__(self) -> str:
        return self.title

class PollOptions(models.Model):
    poll = models.OneToOneField(Poll, on_delete=models.CASCADE)

    random_order = models.BooleanField(default=True)
    authentication_required = models.BooleanField(default=False)

class AuthenticatedPoll(Poll):
    users_have_voted = models.ManyToManyField(User)

    def clean(self) -> None:
        if not self.poll.polloptions.authentication_required: # type: ignore
            raise ValidationError(_("AuthenticatedPoll is only for authenticated polls"))
    
    def require_authentication(self, is_auth) -> bool:
        return not is_auth

    def has_already_voted(self, user) -> bool:
        return self.users_have_voted.filter(pk=user.pk).exists()

    def add_vote(self, user) -> None:
        if not self.has_already_voted(user):
            self.users_have_voted.add(user)