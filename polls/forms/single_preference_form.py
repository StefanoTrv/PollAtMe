from django import forms
from django.db import models
from polls.models import SinglePreference, MajorityOpinionJudgement
from polls.services import SearchPollService

class SinglePreferenceForm(forms.ModelForm):
    class Meta:
        # il modello che vogliamo creare, vogliamo creare una preferenza
        model: type[models.Model] = SinglePreference
        fields: list[str] = ['alternative']

    def __init__(self, poll, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)
        if instance is None:
            self.fields['alternative'] = forms.ModelChoiceField(
                queryset=SearchPollService().get_alternatives_of_a_poll(poll=poll),
                widget=forms.RadioSelect,  # specifichiamo che vogliamo un radio button
                label='Opzioni'
            )

class MajorityOpinionForm(forms.ModelForm):

    form_label: str

    class Meta:
        model: type[models.Model] = MajorityOpinionJudgement
        fields: list[str] = ['grade']
        widgets: dict = {
            'grade': forms.RadioSelect(choices=MajorityOpinionJudgement.JudgeType.choices)
        }
        labels: dict = {
            'grade': ''
        }