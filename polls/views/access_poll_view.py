from django.http import Http404
from django.urls import reverse
from django.views.generic.base import RedirectView


from polls.models.mapping import Mapping
from polls.models.poll import Poll



class AccessPollView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):

        passed_code = kwargs['code'] 

        if Mapping.objects.filter(code=passed_code).count() == 0:
            raise Http404
        
        poll = Mapping.objects.filter(code=passed_code).get().poll ##.pk

        if poll.is_ended():
            self.url = reverse('polls:result', kwargs={'id': poll.pk})
        else:
            self.url = reverse('polls:vote', kwargs={'id': poll.pk})
            
        return super().get_redirect_url(*args, **kwargs)

