from datetime import timedelta
import re

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django import forms
from assertpy import assert_that  # type: ignore
from django.contrib.auth.models import User

from polls.models import Poll, Alternative
from polls.forms import PollFormMain, PollFormAdditionalOptions, BaseAlternativeFormSet
from polls.models.mapping import Mapping

class CreatePollViewTest(TestCase):
    
    url = reverse('polls:create_poll')
    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

    def test_empty(self):
        response = self.client.get(self.url)
        assert_that(response.status_code).is_equal_to(200)

        self.assertTemplateUsed(response, 'polls/create_poll/main_page_create.html')
        assert_that(response).contains_form(PollFormMain)
        assert_that(response).contains_formset(BaseAlternativeFormSet.get_formset_class())
        
    def test_aggiunta_poll(self):
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
        response = self.client.post(self.url, data=step_1_data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed(response, 'polls/create_poll/summary_and_options_create.html')

        # Verifichiamo che ci siano tutti i campi del form
        assert_that(response).contains_form(PollFormAdditionalOptions)

        assert_that(self.client.session.has_key('create')).is_true()
        assert_that(self.client.session['create']).is_length(2)

        now = timezone.localtime(timezone.now())
        step_2_data = step_1_data | {
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.u.id,
            'visibility': 1,
            'save': ''
        }
        response = self.client.post(self.url, data=step_2_data)
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed(response, 'polls/create_poll_success.html')

        assert_that(Poll.objects.count()).is_equal_to(1)
        assert_that(Alternative.objects.count()).is_equal_to(2)
    
    def test_error_on_first_page(self):
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
            'form-1-text': '',
            'form-1-id': '',
            'form-1-DELETE': '',
        }
        response = self.client.post(self.url, data=step_1_data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed(response, 'polls/create_poll/main_page_create.html')
    
    def test_error_on_second_page(self):
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
        self.client.post(self.url, data=step_1_data | {'summary': ''})
        response = self.client.post(self.url, data={'save': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed(response, 'polls/create_poll/summary_and_options_create.html')

    def test_going_back(self):
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
        response = self.client.post(self.url, data=step_1_data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        response = self.client.post(self.url, data={'go_back': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed(response, 'polls/create_poll/main_page_create.html')
        self.assertContains(response,'Lorem ipsum')


    def test_aggiunta_poll_custom_code(self):
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
        response = self.client.post(self.url, data=step_1_data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        now = timezone.localtime(timezone.now())

        step_2_data = step_1_data | {
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.u.id,
            'visibility': 1,
            'save': '',
            'code': 'TestCode',
        }

        response = self.client.post(self.url, data=step_2_data)
        assert_that(response.status_code).is_equal_to(200)

        #testiamo che sia stato salvato il mapping
        assert_that(Mapping.objects.filter(code='TestCode').count()).is_equal_to(1)



    def test_aggiunta_poll_automatic_code(self):
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
        response = self.client.post(self.url, data=step_1_data | {'summary': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        now = timezone.localtime(timezone.now())

        step_2_data = step_1_data | {
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.u.id,
            'visibility': 1,
            'save': '',
            'code': '',
        }

        response = self.client.post(self.url, data=step_2_data)
        assert_that(response.status_code).is_equal_to(200)

        #testiamo che sia stato salvato il mapping

        poll_created = Poll.objects.filter(title = 'Lorem ipsum').get()

        #viene creato il mapping
        assert_that(Mapping.objects.filter(poll=poll_created).count()).is_equal_to(1)

        #viene generato un codice alfanumerico lungo 6
        code = Mapping.objects.filter(poll=poll_created).get().code
        result = bool((re.compile("([a-z]|[A-Z]|\d)*")).fullmatch(code)) and (len(code) == 6)
        assert_that(result).is_true()
