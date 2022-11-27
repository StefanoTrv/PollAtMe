from typing import Any, Dict, Optional
from django import forms
from django.core.exceptions import ValidationError

class CreatePollForm(forms.Form):
    poll_title = forms.CharField(label = 'Titolo', max_length=100)
    poll_text = forms.CharField(widget=forms.Textarea)
    alternative1 = forms.CharField(label = 'Alternativa 1', max_length=100, required=False)
    alternative2 = forms.CharField(label = 'Alternativa 2', max_length=100, required=False)
    alternative3 = forms.CharField(label = 'Alternativa 3', max_length=100, required=False)
    alternative4 = forms.CharField(label = 'Alternativa 4', max_length=100, required=False)
    alternative5 = forms.CharField(label = 'Alternativa 5', max_length=100, required=False)
    alternative6 = forms.CharField(label = 'Alternativa 6', max_length=100, required=False)
    alternative7 = forms.CharField(label = 'Alternativa 7', max_length=100, required=False)
    alternative8 = forms.CharField(label = 'Alternativa 8', max_length=100, required=False)
    alternative9 = forms.CharField(label = 'Alternativa 9', max_length=100, required=False)
    alternative10 = forms.CharField(label = 'Alternativa 10', max_length=100, required=False)

    def clean(self) -> Optional[Dict[str, Any]]:
        form_data = self.cleaned_data
        alternatives_count=0
        if form_data['alternative1'].strip()!='':
            alternatives_count+=1
        if form_data['alternative2'].strip()!='':
            alternatives_count+=1
        if form_data['alternative3'].strip()!='':
            alternatives_count+=1
        if form_data['alternative4'].strip()!='':
            alternatives_count+=1
        if form_data['alternative5'].strip()!='':
            alternatives_count+=1
        if form_data['alternative6'].strip()!='':
            alternatives_count+=1
        if form_data['alternative7'].strip()!='':
            alternatives_count+=1
        if form_data['alternative8'].strip()!='':
            alternatives_count+=1
        if form_data['alternative9'].strip()!='':
            alternatives_count+=1
        if form_data['alternative10'].strip()!='':
            alternatives_count+=1
        if alternatives_count<2:
            raise ValidationError('Non ci sono almeno due alternative.')
        return form_data