from typing import Any, Dict
from django import forms

from polls.models import Poll
from polls.services import SearchPollQueryBuilder
from django.utils.translation import gettext_lazy as _
from datetime import date, datetime, timezone


MONTHS = {
    1: _("Gennaio"),
    2: _("Febbraio"),
    3: _("Marzo"),
    4: _("Aprile"),
    5: _("Maggio"),
    6: _("Giugno"),
    7: _("Luglio"),
    8: _("Agosto"),
    9: _("Settembre"),
    10: _("Ottobre"),
    11: _("Novembre"),
    12: _("Dicembre"),
}

ERROR_MESSAGES = {
    'invalid': 'La data inserita non è valida'
}

class SearchPollForm(forms.Form):
    
    title = forms.CharField(
        label='Titolo',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    range_start_a = forms.DateField(
        label='Data inizio sondaggio da',
        required=False,
        widget=forms.SelectDateWidget(
            attrs={'class': 'form-select'},
            months=MONTHS
        ),
        error_messages=ERROR_MESSAGES
    )
    range_start_b = forms.DateField(
        label='Data inizio sondaggio a',
        required=False,
        widget=forms.SelectDateWidget(
            attrs={'class': 'form-select'},
            months=MONTHS
        ),
        error_messages=ERROR_MESSAGES
    )
    range_end_a = forms.DateField(
        label='Data fine sondaggio da',
        required=False,
        widget=forms.SelectDateWidget(
            attrs={'class': 'form-select'},
            months=MONTHS
        ),
        error_messages=ERROR_MESSAGES
    )
    range_end_b = forms.DateField(
        label='Data fine sondaggio a',
        required=False,
        widget=forms.SelectDateWidget(
            attrs={'class': 'form-select'},
            months=MONTHS
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
        ],
        widget=forms.Select(
            attrs={'class': 'form-select'}
        )
    )
    type = forms.TypedChoiceField(
        coerce=int,
        label="Tipo di sondaggio",
        required=False,
        choices=[(None, '-------'), *Poll.PollType.choices],
        widget=forms.Select(
            attrs={'class': 'form-select'},
        ))

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for f_name in self.fields:
            if self.has_error(f_name):
                widget_class =  self.fields[f_name].widget.attrs['class']
                self.fields[f_name].widget.attrs['class'] = f'{widget_class} is-invalid'

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

        def convert_to_datetime(key: str):
            if form_data.get(key, None) != None:
                saved_date: date = form_data[key]
                form_data[key] = datetime(saved_date.year, saved_date.month, saved_date.day, tzinfo=timezone.utc)
        convert_to_datetime('range_start_a')
        convert_to_datetime('range_start_b')
        convert_to_datetime('range_end_a')
        convert_to_datetime('range_end_b')
        

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
    
    
    