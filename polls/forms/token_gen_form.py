from django import forms

class TokenGeneratorForm(forms.Form):
    tokens_to_be_generated = forms.IntegerField(
        min_value=1,
        max_value=10000,
        label='Inserisci il numero di token da generare'
    )