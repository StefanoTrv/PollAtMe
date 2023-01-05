from typing import Any, Optional

from django.core.exceptions import PermissionDenied
from django.db import models
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from polls.models import Poll


class PollDeleteView(DeleteView):
    model = Poll
    success_url = reverse_lazy('polls:index')
    http_method_names = ['post']

    def get_object(self, queryset: Optional[models.query.QuerySet[Any]] = None) -> models.Model:
        poll: Poll = super().get_object(queryset)

        if not poll.is_not_started():
            raise PermissionDenied('Non è possibile eliminare un sondaggio dopo che la votazione è iniziata')

        return poll
