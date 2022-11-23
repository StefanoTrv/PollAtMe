from django.db import models

class Poll(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self) -> str:
        return self.title+" - "+self.text
    
class Alternative(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    text = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.text

class Preference(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"({self.poll.id}, {self.alternative.id})"