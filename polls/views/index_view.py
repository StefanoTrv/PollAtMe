from typing import Optional, Type

from django.db.models import Model, QuerySet
from polls.models import Poll
from django.views.generic.list import ListView
from polls.services import ActivePollsService

class IndexView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 20
    template_name: str = 'poll_list.html'

    def get_queryset(self) -> QuerySet[Poll]:
        return ActivePollsService().get_queryset()