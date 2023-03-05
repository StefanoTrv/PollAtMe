from django.http import Http404
from django.urls import reverse
from django.views.generic.base import RedirectView


from polls.models.mapping import Mapping


class AccessPollView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):

        passed_code = kwargs['code'] 

        if Mapping.objects.filter(code=passed_code).count() == 0:
            raise Http404
        
        poll_id = Mapping.objects.filter(code=passed_code).get().poll.pk
        self.url = reverse('polls:vote', kwargs={'id': poll_id})
        return super().get_redirect_url(*args, **kwargs)

