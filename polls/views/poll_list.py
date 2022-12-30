from typing import Optional, Type, Any

from django.db.models import Model, QuerySet
from polls.models import Poll
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from polls.services import ActivePollsService
from polls.forms import SearchPollForm

class IndexView(ListView):
    model: Optional[Type[Model]] = Poll
    paginate_by: int = 6
    template_name: str = 'poll_list.html'

    def __init__(self, **kwargs: Any) -> None:
        self.__active_poll_service = ActivePollsService()
        super().__init__(**kwargs)

    def get_queryset(self) -> QuerySet[Poll]:
        return self.__active_poll_service.get_ordered_queryset()

class SearchView(TemplateView):
    template_name: str = 'search_poll.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['form'] = SearchPollForm()
        return context
    