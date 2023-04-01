from django.db import models
from .poll import TokenizedPoll

class Token(models.Model):
    poll = models.ForeignKey(TokenizedPoll, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    used = models.BooleanField(default=False)