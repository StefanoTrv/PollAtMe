from typing import Any

from django import forms
from django.db import models
from django.forms import inlineformset_factory

import polls.models as poll_model


class PreferenceFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.alternatives = kwargs['queryset']

    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['alternative'] = self.alternatives[index]
        return kwargs


class MajorityPreferenceFormSet(PreferenceFormSet):
    @staticmethod
    def get_formset_class(num_judges: int):
        return inlineformset_factory(
            poll_model.Alternative,
            poll_model.MajorityPreference.responses.through,
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
        model: type[models.Model] = poll_model.MajorityOpinionJudgement
        fields: list[str] = ['grade']
        widgets: dict = {
            'grade': forms.RadioSelect(attrs={
                'class': 'btn-check',
            })
        }
        error_messages = {
            'grade': {
                'required': 'Dai un giudizio su questa opzione'
            }
        }

    def __init__(self, *args, **kwargs):
        self.alternative: poll_model.Alternative = kwargs.pop('alternative', None)
        super().__init__(*args, **kwargs)
        self.fields['grade'].label = self.alternative.text
        self.fields['grade'].blank = False
        self.fields['grade'].choices = self.fields['grade'].choices[1:]


    def save(self, commit: bool = ...) -> Any:  # type: ignore
        self.instance.alternative = self.alternative
        return super().save(commit)


class ShultzePreferenceFormSet(PreferenceFormSet):
    @staticmethod
    def get_formset_class(num_judges: int):
        return inlineformset_factory(
            poll_model.Alternative,
            poll_model.preference.ShultzePreference.responses.through,
            form=ShultzeOpinionForm,
            formset=ShultzePreferenceFormSet,
            can_delete=False,
            extra=num_judges,
            max_num=num_judges,
            min_num=num_judges,
            validate_max=True,
            validate_min=True)

class ShultzeOpinionForm(forms.ModelForm):

    class Meta:
        model: type[models.Model] = poll_model.preference.ShultzeOpinionJudgement
        fields: list[str] = ['order']
        widgets: dict = {
            'order': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        self.alternative: poll_model.Alternative = kwargs.pop('alternative', None)
        super().__init__(*args, **kwargs)
        self.fields['order'].label = self.alternative.text
    
    def save(self, commit: bool = ...) -> Any:  # type: ignore
        self.instance.alternative = self.alternative
        return super().save(commit)