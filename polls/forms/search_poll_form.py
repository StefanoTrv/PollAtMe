from django import forms

from polls.models import Poll

class SearchPollForm(forms.Form):
    
    title = forms.CharField()
    range_start_a = forms.DateField()
    range_start_b = forms.DateField()
    range_end_a = forms.DateField()
    range_end_b = forms.DateField()
    status = forms.CharField()
    type = forms.ChoiceField(choices=Poll.PollType.choices)