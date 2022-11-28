from typing import Any

from django import forms
from django.db import models
from django.forms import inlineformset_factory

from polls.models import (Alternative, MajorityOpinionJudgement,
                          MajorityPreference)


class MajorityPreferenceFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.alternatives = kwargs['queryset']

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['alternative'] = self.alternatives[index]
        return kwargs

    @staticmethod
    def get_formset_class(num_judges: int):
        return inlineformset_factory(
            Alternative,
            MajorityPreference.responses.through,
            form=MajorityOpinionForm,
            formset=MajorityPreferenceFormSet,
            can_delete=False,
            extra=num_judges,
            max_num=num_judges,
            min_num=num_judges,
            validate_max=True,
            validate_min=True)


class MajorityOpinionForm(forms.ModelForm):

    class Meta:
        model: type[models.Model] = MajorityOpinionJudgement
        fields: list[str] = ['grade']
        widgets: dict = {
            'grade': forms.RadioSelect(choices=MajorityOpinionJudgement.JudgeType.choices)
        }

    def __init__(self, *args, **kwargs):
        self.alternative: Alternative = kwargs.pop('alternative', None)
        super().__init__(*args, **kwargs)
        self.fields['grade'].label = self.alternative.text

    def save(self, commit: bool = ...) -> Any:  # type: ignore
        self.instance.alternative = self.alternative
        return super().save(commit)
