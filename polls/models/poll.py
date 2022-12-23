from django.db import models


class Poll(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    start = models.DateTimeField(auto_now_add = False, auto_now = False)
    end = models.DateTimeField(auto_now_add = False, auto_now = False)

    def __str__(self) -> str:
        return self.title

class SinglePreferencePoll(Poll):
    pass

class MajorityOpinionPoll(Poll):
    pass
