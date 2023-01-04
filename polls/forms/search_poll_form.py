from typing import Any, Dict
from django import forms

from polls.models import Poll
from polls.services import SearchPollQueryBuilder
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from bootstrap_datepicker_plus import widgets

ERROR_MESSAGES = {
    'invalid': 'La data inserita non è valida'
}

FORMAT = "DD/MM/YYYY"

class SearchPollForm(forms.Form):
    
    title = forms.CharField(
        label='Titolo',
        required=False
    )
    range_start_a = forms.DateTimeField(
        label='Data inizio sondaggio da',
        required=False,
        widget=widgets.DatePickerInput(
            options={
                'format': FORMAT,
            },
        ),
        error_messages=ERROR_MESSAGES
    )
    range_start_b = forms.DateTimeField(
        label='Data inizio sondaggio a',
        required=False,
        widget=widgets.DatePickerInput(
            options={
                'format': FORMAT,
            },
            range_from='range_start_a'
        ),
        error_messages=ERROR_MESSAGES
    )
    range_end_a = forms.DateTimeField(
        label='Data fine sondaggio da',
        required=False,
        widget=widgets.DatePickerInput(
            options={
                'format': FORMAT,
            },
        ),
        error_messages=ERROR_MESSAGES
    )
    range_end_b = forms.DateTimeField(
        label='Data fine sondaggio a',
        required=False,
        widget=widgets.DatePickerInput(
            options={
                'format': FORMAT,
            },
            range_from='range_end_a'
        ),
        error_messages=ERROR_MESSAGES
    )
    status = forms.ChoiceField(
        label='Stato',
        required=False,
        choices=[
            ('', "-------"),
            ('NOT_STARTED', 'In attesa'),
            ('ACTIVE', 'In corso'),
            ('ENDED', 'Concluso'),
        ]
    )
    type = forms.TypedChoiceField(
        coerce=int,
        label="Tipo di sondaggio",
        required=False,
        choices=[(None, '-------'), *Poll.PollType.choices]
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def range_group(self):
        return [self[name] for name in filter(lambda x: x.startswith('range'), self.fields)]

    def clean(self) -> Dict[str, Any]:
        form_data: dict = self.cleaned_data

        range_start_a = form_data.get('range_start_a', None)
        range_start_b = form_data.get('range_start_b', None)
        range_end_a = form_data.get('range_end_a', None)
        range_end_b = form_data.get('range_end_b', None)
        if range_start_a is not None and range_start_b is not None and range_start_a >= range_start_b:
            self.add_error('range_start_a', 'La data di inizio è successiva alla data di fine')

        if range_end_a is not None and range_end_b is not None and range_end_a >= range_end_b:
            self.add_error('range_end_a', 'La data di inizio è successiva alla data di fine')
        
        return form_data
    
    def to_query(self) -> SearchPollQueryBuilder:
        builder = SearchPollQueryBuilder()

        if self.cleaned_data['title'] != '':
            builder.title_filter(self.cleaned_data['title'])
        
        if self.cleaned_data['status'] != '':
            builder.status_filter(self.cleaned_data['status'])
        
        if self.cleaned_data['type'] != '':
            builder.type_filter(self.cleaned_data['type'])
        
        start_range: dict[str, datetime] = {}
        end_range: dict[str, datetime] = {}

        if self.cleaned_data['range_start_a'] is not None:
            start_range['start'] = self.cleaned_data['range_start_a']
        
        if self.cleaned_data['range_start_b'] is not None:
            start_range['end'] = self.cleaned_data['range_start_b']
        
        if self.cleaned_data['range_end_a'] is not None:
            end_range['start'] = self.cleaned_data['range_end_a']
        
        if self.cleaned_data['range_end_b'] is not None:
            end_range['end'] = self.cleaned_data['range_end_b']
        
        if len(start_range) > 0:
            builder.start_range_filter(**start_range)
        
        if len(end_range) > 0:
            builder.end_range_filter(**end_range)

        return builder
    
    
    