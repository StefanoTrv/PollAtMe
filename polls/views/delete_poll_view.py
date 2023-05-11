from typing import Any, Optional

from django.db import models
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from polls.models import Poll
from polls.services import check

from django.contrib.auth.mixins import LoginRequiredMixin


class PollDeleteView(LoginRequiredMixin, DeleteView):
    model = Poll
    success_url = reverse_lazy('polls:personal_polls')
    http_method_names = ['post']

    def get_object(self, queryset: Optional[models.query.QuerySet[Any]] = None) -> models.Model:
        poll: Poll = super().get_object(queryset)

        handler = check.CheckPollIsNotStarted(poll)
        handler.set_next(check.CheckPollOwnership(poll, self.request.user))
        passed = handler.handle()

        return passed if passed else poll
