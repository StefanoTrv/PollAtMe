from datetime import timedelta
from django import forms
from django.utils import timezone

from bootstrap_datepicker_plus.widgets import DateTimePickerInput

from polls.models import Poll, Alternative
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
            'form-MIN_NUM_FORMS': '2',
            'form-MAX_NUM_FORMS':'10',
        }

        for i, alt in enumerate(cleaned_data):
            obj = alt.get('id', None)
            data = data | {
                f'form-{i}-text': alt['text'],
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
            'end': 'Data fine votazioni'
        } | PollFormMain.Meta.labels

        error_messages = {} | PollFormMain.Meta.error_messages
        
        widgets = {
            'start': DateTimePickerInput(
                options={"format": "DD-MM-YYYY HH:mm"}
            ),
            'end': DateTimePickerInput(
                range_from='start',
                options={"format": "DD-MM-YYYY HH:mm"}
            ),
        } | PollFormMain.Meta.widgets
        
        initials = {
            'start': timezone.now() + timedelta(minutes=15),
            'end': timezone.now() + timedelta(weeks=1)
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        for f_name in self.fields:
            if f_name in PollFormMain.Meta.fields:
                self.fields[f_name].widget.attrs['readonly'] = True

    def clean(self):
        form_data = self.cleaned_data

        # errore se il tempo di inizio è precedente ad adesso, con una precisione di 15 minuti
        if form_data['start'] + timedelta(minutes=15) < timezone.now():
            self.add_error('start', 'Il momento di inizio delle votazioni deve essere successivo ad adesso.')

        # errore se il tempo di fine è precedente a cinque minuti da adesso
        if form_data['end'] < timezone.now() + timedelta(minutes=5):
            self.add_error('end', 'Il momento di fine delle votazioni deve essere almeno cinque minuti da adesso.')
        
        if form_data['end'] <= form_data['start']:
            self.add_error('start', 'Il momento di fine delle votazioni deve essere successivo a quello di inizio.')
        elif form_data['end'] < form_data['start'] + timedelta(minutes=5):
            self.add_error('end', 'Il momento di fine delle votazioni deve essere almeno cinque minuti dopo quello di inizio.')

        return form_data
