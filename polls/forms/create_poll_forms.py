import re

from datetime import timedelta
from typing import Any
from django import forms
from django.utils import timezone

from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from polls.models import Poll, Mapping, Alternative, PollOptions

# Form per la pagina principale della pagina di creazione di nuovi sondaggi, contenente i dati principali
class BaseAlternativeFormSet(forms.BaseModelFormSet):
    deletion_widget = forms.HiddenInput
    
    def get_not_empty_alternatives(self):
        return [
            alt
            for alt in self.cleaned_data if len(alt) > 0
        ]

    def get_form_for_session(self) -> dict:
        cleaned_data = self.get_not_empty_alternatives()
        data = {
            'form-TOTAL_FORMS': len(cleaned_data),	
            'form-INITIAL_FORMS': self.data['form-INITIAL_FORMS'],
            'form-MIN_NUM_FORMS': self.data['form-MIN_NUM_FORMS'],
            'form-MAX_NUM_FORMS': self.data['form-MAX_NUM_FORMS'],
        }

        for i, alt in enumerate(cleaned_data):
            obj = alt.get('id', None)
            text = '_' if alt['DELETE'] else alt.get('text', '')
            data = data | {
                f'form-{i}-text': text,
                f'form-{i}-id': obj.id if obj is not None else '',
                f'form-{i}-DELETE': 'true' if alt['DELETE'] else '',
            }

        return data
    
    def get_alternatives_text_list(self) -> list:
        return [
            alt['text'] for alt in self.get_not_empty_alternatives() if alt['DELETE'] is False
        ]

    @staticmethod
    def get_formset_class():
        return forms.modelformset_factory(
            model=Alternative,
            formset=BaseAlternativeFormSet,
            fields=['text'],
            widgets={
                'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Inserisci il testo dell'alternativa"}),
            },
            labels={
                'text': ""
            },
            error_messages={
                'too_few_forms': 'Inserisci almeno %(num)d alternative valide per proseguire',
                'too_many_forms': 'Inserisci al massimo %(num)d alternative valide per proseguire',
            },
            can_order=False, can_delete=True,
            extra=0,
            min_num=2, max_num=10,
            validate_max=True, validate_min=True,
        )


class PollFormMain(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'default_type', 'text']
        labels = {
            'title': 'Titolo',
            'default_type': 'Tipo di scelta',
            'text': 'Testo'
        }
        error_messages = {
            'title': {
                'required': 'Il titolo della scelta non può essere vuoto.'
            }
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Inserisci il titolo della scelta'
            }),
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Inserisci il testo della domanda della scelta (opzionale)'
            })
        }

    def __init__(self, *args, **kwargs):
        super(PollFormMain, self).__init__(*args, **kwargs)
        self.fields['text'].required = False

    def get_temporary_poll(self) -> Poll:
        poll: Poll = self.instance
        if poll.start is None:
            poll.start = timezone.now() + timedelta(minutes=10)
            poll.end = poll.start + timedelta(weeks=1)
        
        if not hasattr(poll, Poll.MAPPING_FIELDNAME):
            poll.mapping = Mapping()
        
        if not hasattr(poll, Poll.OPTIONS_FIELDNAME):
            poll.polloptions = PollOptions()
        
        return self.save(commit=False)

# Form per la seconda pagina della creazione di nuovi sondaggi
class PollForm(forms.ModelForm):
    
    start_now = forms.BooleanField(
        label="Inizia subito (Attenzione: non potrai più modificare o eliminare il sondaggio!)",
        required=False
    )

    class Meta:
        model = Poll
        exclude = ["author"]
        labels = {
            'start': 'Data inizio votazioni',
            'end': 'Data fine votazioni',
            'visibility': "Visibilità",
            'authentication_type': "Modalità di voto",
        } | PollFormMain.Meta.labels

        error_messages = {} | PollFormMain.Meta.error_messages

        widgets = {
            'start': DateTimePickerInput(
                options={"format": "DD-MM-YYYY HH:mm"}
            ),
            'end': DateTimePickerInput(
                options={"format": "DD-MM-YYYY HH:mm"}
            ),
            'default_type': forms.Select(
                attrs={'disabled': True}
            ),
            'text': forms.Textarea(attrs={
                'style': 'resize: none;',
                'rows': 5,
                'placeholder': 'Il testo della scelta verrà lasciato vuoto'
            }),
            'visibility': forms.RadioSelect(
                attrs={
                    'class': 'btn-check'
                }
            ),
            'authentication_type': forms.RadioSelect(
                attrs={
                    'class': 'btn-check'
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['text'].required = False
        self.fields['start'].required = False
        
        for f_name in self.fields:
            if f_name in PollFormMain.Meta.fields:
                self.fields[f_name].widget.attrs['readonly'] = True

    def clean(self):
        if self.errors:
            return
        cleaned_data = self.cleaned_data

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
        start_now = self.cleaned_data['start_now']
        now = timezone.localtime(timezone.now())
        delta = timedelta(minutes=5)

        # se l'utente ha scelto di iniziare il sondaggio subito
        if start_now:
            cleaned_data['start'] = now
            start = cleaned_data['start']
        else:
            # se l'utente non ha scelto di iniziare il sondaggio subito
            # la data di inizio deve essere impostata
            if start is None:
                self.add_error('start', 'Devi impostare la data di inizio del sondaggio')

        if start < now - delta:
            self.add_error('start', 'La data di inizio è precedente a quella attuale')

        if end - start < timedelta(0):
            self.add_error('end', 'La data di fine è precedente alla data di inizio')

        # il sondaggio deve durare almeno 15 minuti
        if end - start < timedelta(minutes=15):
            self.add_error('end', 'La scelta deve durare almeno 15 minuti')

        return cleaned_data


class PollMappingForm(forms.ModelForm):
    class Meta:
        model = Mapping
        exclude = ['poll']
        labels = {
            'code': 'Codice link personalizzato'
        }

        error_messages = {
            'code': {
                'unique': 'Questo codice è già stato utilizzato, prova un altro'
            }
        }

        widgets = {
            'code': forms.TextInput(attrs={
                'placeholder': 'Inserisci un codice alfanumerico per il link (opzionale)'
            })
        }

    def clean_code(self):
        form_code = self.cleaned_data['code']

        #controlliamo se il codice rispetta il vincolo sulla forma
        if not self._code_is_valid(self.cleaned_data['code']):
            self.add_error('code', 'Questo codice non è valido')

        #se nullo generiamo un codice
        if form_code == '':
            form_code = Mapping.generate_code()

        return form_code
    
    def _code_is_valid(self, code):
        pattern = re.compile("([a-z]|[A-Z]|\d)*")
        result = bool(pattern.fullmatch(code))
        return result


class PollOptionsForm(forms.ModelForm):
    class Meta:
        model = PollOptions
        exclude = ['poll']
        labels = {
            'random_order': "Le alternative verranno mostrate in ordine casuale",
        }