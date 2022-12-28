from django.db import models
from django.utils import timezone

class Poll(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    start = models.DateTimeField(auto_now_add = False, auto_now = False)
    end = models.DateTimeField(auto_now_add = False, auto_now = False)

    def is_active(self) -> bool:
        return self.start <= timezone.now() < self.end

    def is_ended(self) -> bool:
        return timezone.now() >= self.end
    
    def is_not_started(self) -> bool:
        return timezone.now() < self.start

    def get_type(self) -> str:
        if hasattr(self, 'singlepreferencepoll'):
            return 'Preferenza singola'
        elif hasattr(self, 'majorityopinionpoll'):
            return 'Giudizio maggioritario'
        else:
            return 'Metodo Shultze'

    def __str__(self) -> str:
        return self.title

class SinglePreferencePoll(Poll):
    pass

class MajorityOpinionPoll(Poll):
    pass
