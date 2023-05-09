from django.db import models

from .alternative import Alternative
from .poll import Poll


class Preference(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    synthetic = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class SinglePreference(Preference):
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.poll.title + ' -> ' + self.alternative.text + ' (' + ('SINTETICO' if self.synthetic else 'REALE') + ')'

class MajorityPreference(Preference):
    # Tra le preferenze e le risposte c'è una relazione many to many mediata
    # dall'indicazione del giudizio
    responses = models.ManyToManyField(Alternative, through="MajorityOpinionJudgement")

    def __str__(self) -> str:
        opinion_list=[]
        for opinion in self.majorityopinionjudgement_set.all():
            opinion_list.append(str(opinion))
        return self.poll.title + ' (preferenza ' + ('SINTETICA' if self.synthetic else 'REALE') + ')'+'\n\t'+'\n\t'.join(opinion_list) +'\n'
    
    @staticmethod
    def save_mj_from_sp(vote: SinglePreference):
        synthetic_preference = MajorityPreference()
        synthetic_preference.poll = vote.poll
        synthetic_preference.synthetic = True
        synthetic_preference.save()

        mojs = [
            MajorityOpinionJudgement(**{
                'alternative': alternative,
                'grade': MajorityOpinionJudgement.JudgementType.OTTIMO if alternative == vote.alternative 
                    else MajorityOpinionJudgement.JudgementType.PESSIMO,
            })
            for alternative in vote.poll.alternative_set.all()
        ]
        synthetic_preference.save_mj_judgements(mojs)
        
        return synthetic_preference
    
    def save_mj_judgements(self, judgments):
        if self.pk:
            self.majorityopinionjudgement_set.all().delete()

        for j in judgments:
            j.preference = self
        MajorityOpinionJudgement.objects.bulk_create(judgments)

class ShultzePreference(Preference):
    responses = models.ManyToManyField(Alternative, through="ShultzeOpinionJudgement")

class MajorityOpinionJudgement(models.Model):
    class JudgementType(models.IntegerChoices):
        """
        Possibili valori per grade
        """
        PESSIMO = 1
        SCARSO = 2
        SUFFICIENTE = 3
        BUONO = 4
        OTTIMO = 5
    
    grade = models.IntegerField(choices=JudgementType.choices)
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    preference = models.ForeignKey(MajorityPreference, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.alternative.text + ' -> ' + str(self.grade)

class ShultzeOpinionJudgement(models.Model):
    order = models.IntegerField()
    alternative = models.ForeignKey(Alternative, on_delete=models.CASCADE)
    preference = models.ForeignKey(ShultzePreference, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.alternative.text + ' -> ' + str(self.order)
