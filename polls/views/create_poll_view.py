from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from polls.forms import CreatePollFormStep1, CreatePollFormStep2, CreatePollFormStep3
from polls.services import add_single_preference_poll, add_majority_judgment_poll

def create_poll_step1(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollFormStep1(request.POST)
        # check whether it's valid:
        if form.is_valid():
            request.session['new_poll_title']=form.cleaned_data['poll_title']
            request.session['new_poll_text']=form.cleaned_data['poll_text']
            request.session['new_poll_alternative_count']=form.cleaned_data['alternative_count']
            return HttpResponseRedirect(reverse('polls:create_poll_step_2'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePollFormStep1()

    return render(request, 'create_poll/step1.html', {'form': form})

def create_poll_step2(request):
    alternative_count : int = request.session['new_poll_alternative_count']
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollFormStep2(alternative_count,request.POST)
        # check whether it's valid:
        if form.is_valid():
            alternatives = []
            for i in range(1,alternative_count+1):
                if form.cleaned_data['alternative'+str(i)].strip()!='':
                    alternatives.append(form.cleaned_data['alternative'+str(i)].strip())
            request.session['new_poll_alternatives']=alternatives
            return HttpResponseRedirect(reverse('polls:create_poll_step_3'))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePollFormStep2(alternative_count)

    return render(request, 'create_poll/step2.html', {'form': form, 'count': alternative_count})

def create_poll_step3(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CreatePollFormStep3(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if form.cleaned_data['poll_type']=='Preferenza singola':
                add_single_preference_poll(request.session['new_poll_title'],request.session['new_poll_text'],request.session['new_poll_alternatives'])
            elif form.cleaned_data['poll_type']=='Giudizio maggioritario':
                add_majority_judgment_poll(request.session['new_poll_title'],request.session['new_poll_text'],request.session['new_poll_alternatives'])
            return render(request, 'create_poll_success.html')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CreatePollFormStep3()

    return render(request, 'create_poll/step3.html', {'form': form, 'title': request.session['new_poll_title']})