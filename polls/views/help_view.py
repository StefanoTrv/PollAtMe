from django.views.generic.base import TemplateView

class ExplanationGMView(TemplateView):
    template_name = "polls/help/spiegazione_giudizio_maggioritario.html"

class HelpSimulatedResultsSpView(TemplateView):
    template_name: str = 'polls/help/help_simulated_results_sp.html'

class HelpSimulatedResultsSchView(TemplateView):
    template_name: str = 'polls/help/help_simulated_results_sch.html'

class ExplanationCreationPollView(TemplateView):
    template_name: str = 'polls/help/help_visibility_and_vote_mode.html'