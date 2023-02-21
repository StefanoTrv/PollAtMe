from django.views.generic.base import TemplateView

class ExplanationGMView(TemplateView):
    template_name = "polls/spiegazione_metodi_voto/spiegazione_giudizio_maggioritario.html"

class HelpSimulatedResultsView(TemplateView):
    template_name: str = 'polls/help_simulated_results.html'