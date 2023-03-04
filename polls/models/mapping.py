from django.db import models

from .poll import Poll


class Mapping(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    link = models.TextField()
    
    def __str__(self) -> str:
        return self.link