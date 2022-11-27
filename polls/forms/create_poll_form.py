from django import forms

class CreatePollForm(forms.Form):
    poll_title = forms.CharField(label = 'Titolo', max_length=50)
    poll_text = forms.CharField(widget=forms.Textarea)