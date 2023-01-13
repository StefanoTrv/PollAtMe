from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Poll


class NewPollSessionCleanerTest(TestCase):
    
    create_url = reverse('polls:create_poll')
    step_1_data = {
            'title': 'Lorem ipsum',
            'text': 'dolor sit amet',
            'default_type': 1,
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
            'form-0-text': 'lorem',
            'form-0-id': '',
            'form-0-DELETE': '',
            'form-1-text': 'ipsum',
            'form-1-id': '',
            'form-1-DELETE': '',
        }
    poll : Poll|None = None
    
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

        self.poll = Poll()
        self.poll.title = 'Sondaggio di prova'
        self.poll.text = 'Sondaggio di prova'
        self.poll.start = timezone.now() + timedelta(weeks=1)
        self.poll.end = timezone.now() + timedelta(weeks=2)
        self.poll.author = self.user
        self.poll.save()
        self.poll.alternative_set.create(text='Alternativa di prova 1')
        self.poll.alternative_set.create(text='Alternativa di prova 2')

    def test_clears_creation(self):
        self.client.post(self.create_url, data=self.step_1_data | {'summary': ''})
        
        self.client.get(reverse('polls:index'))
        response = self.client.get(self.create_url)
        self.assertNotContains(response,'Lorem ipsum')
        
    def test_switch_from_create_to_edit(self):
        self.client.post(self.create_url, data=self.step_1_data | {'summary': ''})
        
        response=self.client.get(reverse('polls:edit_poll',kwargs={'id': self.poll.pk}))
        self.assertNotContains(response,'Lorem ipsum')
        self.assertContains(response,'Sondaggio di prova')


    def test_switch_from_edit_to_create(self):
        self.client.post(reverse('polls:edit_poll',kwargs={'id': self.poll.pk}), data=self.step_1_data | {'summary': ''})
        
        response = self.client.get(self.create_url)
        self.assertNotContains(response,'Lorem ipsum')
        self.assertNotContains(response,'Sondaggio di prova')