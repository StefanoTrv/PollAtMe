from typing import Any, Optional

from django.core.exceptions import PermissionDenied
from django.db import models
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from polls.models import Poll

from django.contrib.auth.mixins import LoginRequiredMixin


class PollDeleteView(LoginRequiredMixin, DeleteView):
    model = Poll
    success_url = reverse_lazy('polls:index')
    http_method_names = ['post']

    def get_object(self, queryset: Optional[models.query.QuerySet[Any]] = None) -> models.Model:
        poll: Poll = super().get_object(queryset)

        if not poll.is_not_started():
            raise PermissionDenied('Non è possibile eliminare un sondaggio dopo che la votazione è iniziata')

        if not poll.author.__eq__(self.request.user):
            raise PermissionDenied('Non hai i permessi per cancellare questo sondaggio')

        return poll
