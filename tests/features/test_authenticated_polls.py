from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from assertpy import assert_that  # type: ignore

from polls import models

class TestAuthenticatedPollsCreate(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')

    # Crea un sondaggio autenticato
    def test_create_authenticated_poll(self):
        self.client.login(username='test', password='test')
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
        response = self.client.post(
            reverse('polls:create_poll'), data=step_1_data | {'summary': ''})
        now = timezone.localtime(timezone.now())

        self.assertContains(response, "L'utente deve aver effettuato il login per votare")

        step_2_data = step_1_data | {
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.u.id,
            'visibility': 1,
            'authentication_required': '',
            'save': ''
        }
        response = self.client.post(reverse('polls:create_poll'), data=step_2_data)
        assert_that(response.status_code).is_equal_to(200)

        try:
            p = models.Poll.objects.get(title='Lorem ipsum')
        except models.Poll.DoesNotExist:
            self.fail('Poll was not created')
        assert_that(p.polloptions.authentication_required).is_true()

        try:
            models.AuthenticatedPoll.objects.get(poll=p)
        except models.AuthenticatedPoll.DoesNotExist:
            self.fail('AuthenticatedPoll was not created')
    

class TestAuthenticatedPollsVote(TestCase):
    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')
        self.ap = models.AuthenticatedPoll()
        self.ap.title = 'Lorem ipsum'
        self.ap.text = 'dolor sit amet'
        self.ap.default_type = models.Poll.PollType.SINGLE_PREFERENCE
        self.ap.author = self.u
        self.ap.start = timezone.localtime(timezone.now()) + timedelta(minutes=20)
        self.ap.end = timezone.localtime(timezone.now()) + timedelta(weeks=1)
        self.ap.visibility = models.Poll.PollVisibility.HIDDEN
        self.ap.polloptions.authentication_required = True
        self.ap.save()

        self.ap.alternative_set.create(text='lorem')
        self.ap.alternative_set.create(text='ipsum')

    '''
    Se un utente non autenticato prova a votare un sondaggio che richiede l'autenticazione deve essere rimandato alla pagina di autenticazione, in questo caso deve essere anche presente un messaggio che faccia capire all'utente che per tale sondaggio è richiesta l'autenticazione. 
    '''
    def test_try_to_vote_without_authentication(self):
        response = self.client.get(reverse('polls:access_poll', args=[self.ap.mapping.code]))
        self.assertContains(response, "L'utente deve aver effettuato il login per votare")
        assert_that(response.url).is_equal_to(reverse('login') + '?next=' + reverse('polls:vote', args=[self.ap.id]))
    
    def test_try_to_vote_authenticate(self):
        self.client.login(username='test', password='test')
        response = self.client.get(reverse('polls:access_poll', args=[self.ap.mapping.code]))
        assert_that(response.url).is_equal_to(reverse('polls:vote', args=[self.ap.id]))
        