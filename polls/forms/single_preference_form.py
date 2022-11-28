from django import forms
from django.db import models

from polls.models import SinglePreference, SinglePreferencePoll
from polls.services import SearchPollService


class SinglePreferenceForm(forms.ModelForm):
    class Meta:
        # il modello che vogliamo creare, vogliamo creare una preferenza
        model: type[models.Model] = SinglePreference
        fields: list[str] = ['alternative']

    def __init__(self, *args, **kwargs) -> None:
        poll: SinglePreferencePoll = kwargs.pop('poll', None)
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)
        if instance is None:
            self.fields['alternative'] = forms.ModelChoiceField(
                queryset=poll.alternative_set.all(),
                widget=forms.RadioSelect,  # specifichiamo che vogliamo un radio button
                label='Opzioni'
            )
