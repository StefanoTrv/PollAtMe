from typing import Optional, Type, Any

from django.db.models import Model, QuerySet
from polls.models import Poll
from django.views.generic.list import ListView
from polls.services import ActivePollsService

class IndexView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 1
    template_name: str = 'poll_list.html'

    def __init__(self, **kwargs: Any) -> None:
        self.__active_poll_service = ActivePollsService()
        super().__init__(**kwargs)

    def get_queryset(self) -> list[QuerySet[Poll]]:
        return self.__active_poll_service.get_ordered_queryset()