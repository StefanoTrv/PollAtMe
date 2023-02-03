from django.shortcuts import render

def explain_majority_judgement(request):
    return render(request, 'polls/spiegazione_metodi_voto/spiegazione_giudizio_magioritario.html')