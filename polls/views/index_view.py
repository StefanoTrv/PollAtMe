from typing import Optional, Type

from polls.models import Question
from django.db.models import Model, QuerySet, Count
from django.views.generic.list import ListView

class IndexView(ListView):
    model: Optional[Type[Model]] = Question
    paginate_by: int = 20
    template_name: str = "question_list.html"

    def get_queryset(self) -> QuerySet[Question]:
        return Question.objects.annotate(num_choices=Count('choice')).filter(num_choices__gt=0).order_by('question_text')