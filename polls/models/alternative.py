from django.db import models

from .poll import Poll


class Alternative(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.text