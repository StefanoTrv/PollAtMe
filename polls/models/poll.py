from django.db import models

class Poll(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self) -> str:
        return self.title

class SinglePreferencePoll(Poll):
    pass

class MajorityOpinionPoll(Poll):
    pass
