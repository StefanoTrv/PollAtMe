from django.http import HttpResponseRedirect
from django.shortcuts import render

from polls.forms import CreatePollForm
from polls.services import add_single_preference_poll

def create_poll(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            alternatives = []
            if form.cleaned_data['alternative1'].strip()!='':
                alternatives.append(form.cleaned_data['alternative1'].strip())
            if form.cleaned_data['alternative2'].strip()!='':
                alternatives.append(form.cleaned_data['alternative2'].strip())
            if form.cleaned_data['alternative3'].strip()!='':
                alternatives.append(form.cleaned_data['alternative3'].strip())
            if form.cleaned_data['alternative4'].strip()!='':
                alternatives.append(form.cleaned_data['alternative4'].strip())
            if form.cleaned_data['alternative5'].strip()!='':
                alternatives.append(form.cleaned_data['alternative5'].strip())
            if form.cleaned_data['alternative6'].strip()!='':
                alternatives.append(form.cleaned_data['alternative6'].strip())
            if form.cleaned_data['alternative7'].strip()!='':
                alternatives.append(form.cleaned_data['alternative7'].strip())
            if form.cleaned_data['alternative8'].strip()!='':
                alternatives.append(form.cleaned_data['alternative8'].strip())
            if form.cleaned_data['alternative9'].strip()!='':
                alternatives.append(form.cleaned_data['alternative9'].strip())
            if form.cleaned_data['alternative10'].strip()!='':
                alternatives.append(form.cleaned_data['alternative10'].strip())
            add_single_preference_poll(form.cleaned_data['poll_title'],form.cleaned_data['poll_text'],alternatives)
            return render(request, 'create_poll_success.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePollForm()

    return render(request, 'create_poll.html', {'form': form})