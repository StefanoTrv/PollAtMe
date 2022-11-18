from django.db import models

class Poll(models.Model):
    question_text = models.TextField()

    def __str__(self) -> str:
        return self.question_text[:20]
    

class Choice(models.Model):
    question = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.choice_text

class Vote(models.Model):
    question = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"({self.question.id}, {self.choice.id})"