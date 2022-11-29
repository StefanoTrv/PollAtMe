from django import forms
from django.core.exceptions import ValidationError

class CreatePollFormStep1(forms.Form):
    poll_title = forms.CharField(label = 'Titolo', max_length=100)
    poll_text = forms.CharField(label = 'Testo', widget=forms.Textarea)
    alternative_count = forms.IntegerField(label = 'Numero di alternative', min_value=2, max_value=10)



class CreatePollFormStep2(forms.Form):
    def __init__(self, alternative_count : int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for i in range(alternative_count):
            self.fields['alternative'+str(i+1)]=forms.CharField(label = 'Alternativa '+str(i+1), max_length=100)

class CreatePollFormStep3(forms.Form):
    poll_type = forms.ChoiceField(choices=[
        ('Preferenza singola', 'Preferenza singola'),
    ])