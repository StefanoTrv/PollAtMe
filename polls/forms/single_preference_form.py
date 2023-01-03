from django import forms
from django.db import models

from polls.models import SinglePreference, Poll


class SinglePreferenceForm(forms.ModelForm):
    class Meta:
        # il modello che vogliamo creare, vogliamo creare una preferenza
        model: type[models.Model] = SinglePreference
        fields: list[str] = ['alternative']

    def __init__(self, *args, **kwargs) -> None:
        poll: Poll = kwargs.pop('poll', None)
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance", None)
        if instance is None:
            self.fields['alternative'] = forms.ModelChoiceField(
                queryset=poll.alternative_set.all(),
                widget=forms.RadioSelect(attrs={
                    'class': 'form-check-input'
                }),  # specifichiamo che vogliamo un radio button
                label=''
            )
