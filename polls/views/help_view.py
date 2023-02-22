from django.views.generic.base import TemplateView

class ExplanationGMView(TemplateView):
    template_name = "polls/help/spiegazione_giudizio_maggioritario.html"

class HelpSimulatedResultsView(TemplateView):
    template_name: str = 'polls/help/help_simulated_results.html'