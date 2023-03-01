from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

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
    text = models.TextField()
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

    def __str__(self) -> str:
        return self.title
    
    def is_public(self) -> bool:
        return self.visibility == Poll.PollVisibility.PUBLIC
