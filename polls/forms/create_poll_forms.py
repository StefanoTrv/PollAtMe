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
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '2',
            'form-MAX_NUM_FORMS':'10',
        }

        for i, alt in enumerate(cleaned_data):
            obj = alt.get('id', None)
            poll = alt.get('poll', None)
            data = data | {
                f'form-{i}-text': alt['text'],
                f'form-{i}-id': obj.id if obj is not None else "",
                f'form-{i}-poll': poll.id if poll is not None else "",
                f'form-{i}-DELETE': alt['DELETE'],
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
            fields=['text', 'poll'],
            widgets={
                'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "inserisci il testo dell'alternativa"}),
                'poll': forms.HiddenInput()
            },
            labels={
                'text': ""
            },
            can_order=False, can_delete=True,
            extra=0,
            min_num=2, max_num=10,
            validate_max=True, validate_min=True)


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
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        for f_name in self.fields:
            if f_name in PollFormMain.Meta.fields:
                self.fields[f_name].widget.attrs['readonly'] = True

    # start_time = forms.DateTimeField(
    #     label='Data inizio votazioni',
    #     initial=timezone.now() + timedelta(minutes=15),
    #     widget=DateTimePickerInput(
    #         options={"format": "DD-MM-YYYY HH:mm"}
    #     )
    # )

    # end_time = forms.DateTimeField(
    #     label='Data fine votazioni',
    #     widget=DateTimePickerInput(
    #         range_from="start_time",
    #         options={"format": "DD-MM-YYYY HH:mm"}
    #     )
    # )  # durata di default: 1 settimana

    # # Può ricevere i parametri 'start_time', 'end_time' e 'poll'. Se quest'ultimo è presente, sovrascrive tutti i precedenti.
    # def __init__(self, *args, **kwargs):
    #     start_time = kwargs.pop('start_time', None)
    #     end_time = kwargs.pop('end_time', None)

    #     poll = kwargs.pop('poll', None)
    #     if poll != None:
    #         start_time = poll.start
    #         end_time = poll.end

    #     super(PollFormAdditionalOptions, self).__init__(*args, **kwargs)

    #     if start_time != None:
    #         self.fields['start_time'].initial = start_time

    #     if end_time != None:
    #         self.fields['end_time'].initial = end_time

    # def clean(self):
    #     form_data = self.cleaned_data

    #     # errore se il tempo di inizio è precedente ad adesso, con una precisione di 15 minuti
    #     if form_data['start_time'] + timedelta(minutes=15) < timezone.now():
    #         self.add_error(
    #             None, 'Il momento di inizio delle votazioni deve essere successivo ad adesso.')
    #     # errore se il tempo di fine è precedente a cinque minuti da adesso
    #     if form_data['end_time'] < timezone.now() + timedelta(minutes=5):
    #         self.add_error(
    #             None, 'Il momento di fine delle votazioni deve essere almeno cinque minuti da adesso.')
    #     # errore se il tempo di fine è precedente al tempo di inizio
    #     if form_data['end_time'] < form_data['start_time']:
    #         self.add_error(
    #             None, 'Il momento di fine delle votazioni deve essere successivo a quello di inizio.')
    #     # errore se non ci sono almeno cinque minuti di differenza tra i due tempi
    #     elif form_data['end_time'] < form_data['start_time'] + timedelta(minutes=5):
    #         self.add_error(
    #             None, 'Il momento di fine delle votazioni deve essere almeno cinque minuti dopo quello di inizio.')

    #     return form_data
