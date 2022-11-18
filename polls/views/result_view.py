from django.db import models
from django.db.models import Count
from django.db.models.query import QuerySet
from django.views.generic.list import ListView

from polls.models import Choice, Vote
from polls.services import PollResultsService


class SinglePreferenceListView(ListView):

    model: type[models.Model] = Vote
    template_name: str = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = PollResultsService(self.kwargs['id']).as_list()
        context['poll_id'] = self.kwargs['id']
        return context