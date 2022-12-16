from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from polls.models import Poll

class PollDeleteView(DeleteView):
    model = Poll
    success_url = reverse_lazy('polls:index')
    http_method_names = ['post']
