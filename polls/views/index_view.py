from typing import Optional, Type, Any

from django.db.models import Model, QuerySet
from polls.models import Poll
from django.views.generic.list import ListView
from polls.services import ActivePollsService

from django.http import HttpResponseRedirect
from django.urls import reverse

class IndexView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 50
    template_name: str = 'poll_list.html'

    def __init__(self, **kwargs: Any) -> None:
        self.__active_poll_service = ActivePollsService()
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['object_list'] = zip([
            'Preferenza singola',
            'Giudizio maggioritario',
            'Metodo Shultze'
        ], context['object_list'])
        return context

    def get_queryset(self) -> list[QuerySet[Poll]]:
        return self.__active_poll_service.get_ordered_queryset()