from datetime import timedelta
from django import forms
from polls.models import SinglePreferencePoll, MajorityOpinionPoll
from django.utils import timezone

# Form per la pagina principale della pagina di creazione di nuovi sondaggi, contenente i dati principali


class CreatePollFormMain(forms.Form):

    poll_title = forms.CharField(
        label='Titolo',
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Inserisci il titolo del sondaggio'}))

    poll_type = forms.ChoiceField(
        label='Tipo di sondaggio',
        widget=forms.Select(attrs={'class': 'form-select'}),
        choices=[
            ('Giudizio maggioritario', 'Giudizio maggioritario'),
            ('Preferenza singola', 'Preferenza singola'),
        ])

    poll_text = forms.CharField(label='Testo',
                                widget=forms.Textarea(attrs={
                                    'class': 'form-control',
                                    'rows': '4',
                                    'placeholder': 'Inserisci il testo della domanda del sondaggio'
                                }))

    # sia quelle attive che quelle che l'utente ha cancellato, ma che in realtà sono solo nascoste
    hidden_alternative_count = forms.IntegerField(widget=forms.HiddenInput())

    # Senza argomenti i campi sono tutti vuoti.
    # Può ricevere i parametri 'poll_title', 'poll_text', 'poll_type', 'alternatives' e 'poll'. Se quest'ultimo è presente, sovrascrive tutti i precedenti.
    def __init__(self, *args, **kwargs):
        number_of_alternatives = int(kwargs.pop('count', 2))

        poll_title = kwargs.pop('poll_title', None)
        poll_text = kwargs.pop('poll_text', None)
        poll_type = kwargs.pop('poll_type', None)

        alternatives = kwargs.pop('alternatives', [])

        if 'poll' in kwargs:
            poll = kwargs.pop('poll')
            # è necessario fare query sul db per scoprire il tipo del sondaggio
            if len(SinglePreferencePoll.objects.filter(id=poll.id)) == 1:
                poll_type = 'Preferenza singola'
            elif len(MajorityOpinionPoll.objects.filter(id=poll.id)) == 1:
                poll_type = 'Giudizio maggioritario'
            else:
                raise TypeError
            poll_title = poll.title
            poll_text = poll.text
            alternatives = [a.text for a in poll.alternative_set.all()]

        super(CreatePollFormMain, self).__init__(*args, **kwargs)
        self.fields['hidden_alternative_count'].initial = max(
            number_of_alternatives, len(alternatives))

        self.fields['poll_title'].initial = poll_title
        self.fields['poll_text'].initial = poll_text
        self.fields['poll_type'].initial = poll_type

        for index in range(max(number_of_alternatives, len(alternatives))):
            # generate extra fields in the number specified via hidden_alternative_count and enough for all the alternatives passed as input (that is, the max of the two)
            self.fields[f'alternative{index+1}'] = forms.CharField(
                label='Alternativa',
                max_length=100,
                required=False,
                widget=forms.TextInput(
                    attrs={'class': 'form-control',
                           'placeholder': 'Inserisci il testo dell\'alternativa'}
                )
            )

        for index in range(len(alternatives)):
            self.fields[f'alternative{index+1}'].initial = alternatives[index]

    def set_errors(self, errors):
        for error in errors:
            self.add_error(error)

    def clean(self):
        form_data = self.cleaned_data

        # rimuovo le alternative vuote
        alternatives = []
        for i in range(1, form_data['hidden_alternative_count'] + 1):
            if form_data[f'alternative{i}'].strip() != "":
                alternatives.append(form_data[f'alternative{i}'].strip())
            del form_data[f'alternative{i}']
        form_data['hidden_alternative_count'] = len(alternatives)
        for i in range(len(alternatives)):
            form_data[f'alternative{i+1}'] = alternatives[i]

        # errore se il campo del titolo è vuoto
        if 'poll_title' not in form_data:
            self.add_error(None, "Il titolo non può essere vuoto.")

        # errore se non ci sono abbastanza alternative
        if form_data['hidden_alternative_count'] not in range(2, 10):
            self.add_error(
                None, "Il numero di alternative deve essere compreso tra 2 e 10.")

        # errore se il campo del testo è vuoto
        if 'poll_text' not in form_data:
            self.add_error(
                None, "Il testo del sondaggio non può essere vuoto.")

        return form_data
    
    def alternatives_group(self):
        return [self[name] for name in filter(lambda x: x.startswith('alternative'), self.fields.values())]

# Form per la seconda pagina della creazione di nuovi sondaggi, contenente opzioni secondarie


# per ora vuota, sarà da riempire con le opzioni
class CreatePollAdditionalOptions(forms.Form):
    
    start_time = forms.DateTimeField(
        label='Data inizio votazioni', 
        initial=timezone.now(), 
        input_formats=['%d/%m/%Y %H:%M']
    )
    
    end_time = forms.DateTimeField(
        label='Data fine votazioni',
        initial=timezone.now() + timedelta(weeks=1),
        input_formats=['%d/%m/%Y %H:%M']
    )  # durata di default: 1 settimana

    # Può ricevere i parametri 'start_time', 'end_time' e 'poll'. Se quest'ultimo è presente, sovrascrive tutti i precedenti.
    def __init__(self, *args, **kwargs):
        start_time = kwargs.pop('start_time', None)
        end_time = kwargs.pop('end_time', None)

        poll = kwargs.pop('poll', None)
        if poll != None:
            start_time = poll.start
            end_time = poll.end

        super(CreatePollAdditionalOptions, self).__init__(*args, **kwargs)

        if start_time != None:
            self.fields['start_time'].initial = start_time

        if end_time != None:
            self.field['end_time'].initial = end_time

    def clean(self):
        form_data = self.cleaned_data

        print("test")
        print(form_data)

        # errore se il tempo di inizio è precedente ad adesso, con una precisione di 15 minuti
        # aggiungo informazioni sulla timezone per poter fare il confronto
        if form_data['start_time'] + timedelta(minutes=15) < timezone.now():
            self.add_error(
                None, "Il momento di inizio delle votazioni deve essere successivo ad adesso.")

        # errore se il tempo di fine è precedente a cinque minuti da adesso
        if form_data['end_time'] < timezone.now() + timedelta(minutes=5):
            self.add_error(
                None, "Il momento di fine delle votazioni deve essere almeno cinque minuti da adesso.")

        # errore se il tempo di fine è precedente al tempo di inizio
        if form_data['end_time'] < form_data['start_time']:
            self.add_error(
                None, "Il momento di fine delle votazioni deve essere successivo a quello di inizio.")
        # errore se non ci sono almeno cinque minuti di differenza tra i due tempi
        elif form_data['end_time'] < form_data['start_time'] + timedelta(minutes=5):
            self.add_error(
                None, "Il momento di fine delle votazioni deve essere almeno cinque minuti dopo quello di inizio.")

        return form_data
