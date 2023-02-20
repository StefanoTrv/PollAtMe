from django.views.generic import TemplateView

class HelpSimulatedResultsView(TemplateView):
    template_name: str = 'polls/help_simulated_results.html'