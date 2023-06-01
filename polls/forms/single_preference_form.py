from django import forms
from django.db import models

from polls.models import SinglePreference, Poll


class SinglePreferenceForm(forms.ModelForm):
    """
    A form class for capturing a single preference in a poll.

    This form is used to create or update a SinglePreference instance.
    It contains a field for selecting an alternative from the available options.
    """

    class Meta:
        """
        Meta class defining the model and fields used in the form.

        The form is associated with the SinglePreference model, and only the 'alternative' field is included.
        """
        model: type[models.Model] = SinglePreference
        fields: list[str] = ['alternative']

    def __init__(self, *args, **kwargs) -> None:
        poll: Poll = kwargs.pop('poll', None)
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance', None)
        if instance is None:
            self.fields['alternative'] = forms.ModelChoiceField(
                queryset=poll.alternative_set.all(),
                widget=forms.RadioSelect(attrs={
                    'class': 'btn-check'
                }),
                label=''
            )
