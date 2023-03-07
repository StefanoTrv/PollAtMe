import re

from datetime import timedelta
from django import forms
from django.utils import timezone

from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from polls.models import Poll, Mapping, Alternative

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
                'too_few_forms': 'Inserisci almeno %(num)d alternative valide per proseguire'
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
            'default_type': 'Tipo di sondaggio',
            'text': 'Testo'
        }
        error_messages = {
            'title': {
                'required': 'Il testo del sondaggio non può essere vuoto.'
            },
            'text': {
                'required': 'Il testo del sondaggio non può essere vuoto.'
            }
        }

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Inserisci il titolo del sondaggio'
            }),
            'text': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Inserisci il testo della domanda del sondaggio'
            })
        }


# Form per la seconda pagina della creazione di nuovi sondaggi, contenente opzioni secondarie
class PollFormAdditionalOptions(forms.ModelForm):
    class Meta:
        model = Poll
        fields = "__all__"
        labels = {
            'start': 'Data inizio votazioni',
            'end': 'Data fine votazioni',
            'visibility': "Visibilità"
        } | PollFormMain.Meta.labels

        error_messages = {} | PollFormMain.Meta.error_messages
        
        widgets = {
            'author': forms.HiddenInput(),
            'start': DateTimePickerInput(
                options={"format": "DD-MM-YYYY HH:mm"}
            ),
            'end': DateTimePickerInput(
                range_from='start',
                options={"format": "DD-MM-YYYY HH:mm"}
            ),
            'default_type': forms.Select(
                attrs={'disabled': True}
            ),
            'text': forms.Textarea(attrs={
                'style': 'resize: none;',
                'rows': 4
            }),
            'visibility': forms.RadioSelect(
                choices=[
                    ('1', 'Nascosto'),
                    ('2', 'Pubblico'),
                ],
                attrs={
                    'class': 'btn-check'
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        for f_name in self.fields:
            if f_name in PollFormMain.Meta.fields:
                self.fields[f_name].widget.attrs['readonly'] = True

    def clean(self):
        if self.errors:
            return

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']

        now = timezone.localtime(timezone.now())

        if end - start < timedelta(0):
            self.add_error('end', 'La data di fine è precedente alla data di inizio')

        # il sondaggio deve iniziare almeno 5 minuti da adesso
        if start - now < timedelta(minutes=5):
            self.add_error('start', 'Il sondaggio deve iniziare almeno 5 minuti da adesso')

        # il sondaggio deve durare almeno 15 minuti
        if end - start < timedelta(minutes=15):
            self.add_error('end', 'Il sondaggio deve durare almeno 15 minuti')

        return self.cleaned_data


class PollMappingForm(forms.ModelForm):
    class Meta:
        model = Mapping
        fields = ['code']
        labels = {
            'code': 'Codice link personalizzato'
        }

        widgets = {
            'code': forms.Textarea(attrs={
                'style': 'resize: none;',
                'rows': 1
            })
        }

    def clean(self):
        if self.errors:
            return

        form_code = self.cleaned_data['code']

        #controlliamo se il codice rispetta il vincolo sulla forma
        if not self._code_is_valid(self.cleaned_data['code']):
            self.add_error('code', 'Questo codice non è valido')

        elif Mapping.objects.filter(code=form_code).count() > 0:
            self.add_error('code', 'Questo codice è già stato utilizzato, prova un altro')

        #se nullo generiamo un codice
        elif not self.cleaned_data['code']:
            self.cleaned_data['code'] = Mapping.generate_code()

        return self.cleaned_data
    
    def _code_is_valid(self, code):
        pattern = re.compile("([a-z]|[A-Z]|\d)*")
        result = bool(pattern.fullmatch(code))
        return result
    