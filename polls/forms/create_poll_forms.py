from django import forms

#Form per la pagina principale della pagina di creazione di nuovi sondaggi, contenente i dati principali
class CreatePollFormMain(forms.Form):
    poll_title = forms.CharField(label = 'Titolo', max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Inserisci il titolo del sondaggio'}))
    poll_type = forms.ChoiceField(label = 'Tipo di sondaggio', choices=[
        ('Giudizio maggioritario', 'Giudizio maggioritario'),
        ('Preferenza singola', 'Preferenza singola'),
    ], widget=forms.Select(attrs={'class':'form-control'}))
    poll_text = forms.CharField(label = 'Testo', widget=forms.Textarea(attrs={'class':'form-control', 'rows':'4', 'placeholder':'Inserisci il testo della domanda del sondaggio'}))
    hidden_alternative_count = forms.IntegerField(widget=forms.HiddenInput())#sia quelle attive che quelle che l'utente ha cancellato, ma che in realtà sono solo nascoste

    def __init__(self, *args, **kwargs):
        number_of_alternatives = int(kwargs.pop('count', 2))

        poll_title = kwargs.pop('poll_title',None)
        poll_text = kwargs.pop('poll_text',None)
        poll_type = kwargs.pop('poll_type',None)

        alternatives = kwargs.pop('alternatives',[])

        super(CreatePollFormMain, self).__init__(*args, **kwargs)
        self.fields['hidden_alternative_count'].initial = max(number_of_alternatives,len(alternatives))

        self.fields['poll_title'].initial = poll_title
        self.fields['poll_text'].initial = poll_text
        self.fields['poll_type'].initial = poll_type

        for index in range(max(number_of_alternatives,len(alternatives))):
            # generate extra fields in the number specified via hidden_alternative_count and enough for all the alternatives passed as input (that is, the max of the two)
            self.fields['alternative'+str(index+1)] = forms.CharField(label = 'Alternativa', max_length=100, required=False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Inserisci il testo dell\'alternativa'}))
        
        for index in range(len(alternatives)):
            self.fields['alternative'+str(index+1)].initial=alternatives[index]
    
    def clean(self):
        form_data = self.cleaned_data

        #rimuovo le alternative vuote
        alternatives=[]
        for i in range(1,form_data['hidden_alternative_count']+1):
            if form_data['alternative'+str(i)].strip()!="":
                alternatives.append(form_data['alternative'+str(i)].strip())
            del form_data['alternative'+str(i)]
        form_data['hidden_alternative_count']=len(alternatives)
        for i in range(len(alternatives)):
            form_data['alternative'+str(i+1)]=alternatives[i]
        
        #errore se il campo del titolo è vuoto
        if 'poll_title' not in form_data:
            self.add_error(None, "Il titolo non può essere vuoto.")

        #errore se non ci sono abbastanza alternative
        if form_data['hidden_alternative_count'] not in range (2,10):
            self.add_error(None, "Il numero di alternative deve essere compreso tra 2 e 10.")
        
        #errore se il campo del testo è vuoto
        if 'poll_text' not in form_data:
            self.add_error(None, "Il testo del sondaggio non può essere vuoto.")
        return form_data

#Form per la seconda pagina della creazione di nuovi sondaggi, contenente opzioni secondarie
class CreatePollAdditionalOptions(forms.Form):#per ora vuota, sarà da riempire con le opzioni
    pass