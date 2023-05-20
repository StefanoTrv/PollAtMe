from django.views.generic.base import TemplateView

class ExplanationGMView(TemplateView):
    template_name = "polls/help/spiegazione_giudizio_maggioritario.html"

class ExplanationSchView(TemplateView):
    template_name = "polls/help/spiegazione_schultze.html"

class HelpSimulatedResultsView(TemplateView):
    template_name: str = 'polls/help/help_simulated_results.html'

class ExplanationCreationPollView(TemplateView):
    template_name: str = 'polls/help/help_advanced_options.html'