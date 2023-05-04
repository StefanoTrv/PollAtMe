from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic.base import RedirectView

from polls.models.mapping import Mapping


class AccessPollView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):

        mapping = get_object_or_404(Mapping, code=kwargs['code'])
        
        poll = mapping.poll

        if poll.is_ended():
            self.url = reverse('polls:result', kwargs={'id': poll.pk})
        else:
            if 'token' in kwargs:
                redirect_args = {'id': poll.pk, 'token': kwargs['token']}
            else:
                redirect_args={'id': poll.pk}
            self.url = reverse('polls:vote', kwargs=redirect_args)
            
        return super().get_redirect_url(*args, **kwargs)

