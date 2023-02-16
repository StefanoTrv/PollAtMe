from django.views.generic.base import TemplateView

class ExplanationGMView(TemplateView):
    template_name = "polls/spiegazione_metodi_voto/spiegazione_giudizio_magioritario.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context