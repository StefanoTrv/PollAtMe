from django.db import models
from .alternative import Alternative
from .poll import Poll

class Preference(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return str(self.id)

class SinglePreference(Preference):
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)

class MajorityPreference(Preference):
    # Tra le preferenze e le risposte c'è una relazione many to many mediata
    # dall'indicazione del giudizio
    responses = models.ManyToManyField(Alternative, through="MajorityOpinionJudgement")

class MajorityOpinionJudgement(models.Model):
    class JudgeType(models.IntegerChoices):
        """
        Possibili valori per grade
        """
        PESSIMO = 1
        MEDIOCRE = 2
        BUONO = 3
        DISCRETO = 4
        OTTIMO = 5
    
    grade = models.IntegerField(choices=JudgeType.choices)
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    preference = models.ForeignKey(MajorityPreference, on_delete=models.CASCADE)
