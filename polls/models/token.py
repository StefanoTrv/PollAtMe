from django.db import models

class Token(models.Model):
    poll = models.ForeignKey('TokenizedPoll', on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return "\""+self.token+"\" -> "+str(self.poll)+" ("+str(self.used)+")"