from django import forms

class TokenGeneratorForm(forms.Form):
    tokens_to_be_generated = forms.IntegerField(
        min_value=1,
        max_value=20,
        label='Inserisci il numero di password da generare'
    )