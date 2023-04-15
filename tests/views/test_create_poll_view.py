from datetime import timedelta
import re

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from assertpy import assert_that  # type: ignore
from django.contrib.auth.models import User

from polls.models import Poll, Alternative, PollOptions, Mapping
from polls.forms import PollFormMain, PollForm, BaseAlternativeFormSet, PollMappingForm, PollOptionsForm

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
            'summary': ''
        }

        now = timezone.localtime(timezone.now())
        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'visibility': Poll.PollVisibility.HIDDEN.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'random_order': False,
            'save': ''
        }

        response = self.client.post(self.url, data=step_1_data)
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed(response, 'polls/create_poll/summary_and_options_create.html')

        # Verifichiamo che ci siano tutti i campi del form
        assert_that(response).contains_form(PollForm)
        assert_that(response).contains_form(PollMappingForm)
        assert_that(response).contains_form(PollOptionsForm)

        response = self.client.post(self.url, data=step_2_data)
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse('polls:poll_created_success'))

        assert_that(Poll.objects.count()).is_equal_to(1)
        assert_that(Alternative.objects.count()).is_equal_to(2)
        assert_that(Mapping.objects.count()).is_equal_to(1)
        assert_that(PollOptions.objects.count()).is_equal_to(1)

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
            'summary': ''
        }

        now = timezone.now()
        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'visibility': Poll.PollVisibility.HIDDEN.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'random_order': False,
        }

        response = self.client.post(self.url, data=step_1_data)
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        # torno indietro alla prima pagina
        response = self.client.post(self.url, data=step_2_data | {'go_back': ''})
        self.assertContains(response, step_1_data['title'])
        self.assertContains(response, step_1_data['text'])
        self.assertContains(response, step_1_data['default_type'])
        self.assertContains(response, step_1_data['form-0-text'])
        self.assertContains(response, step_1_data['form-1-text'])

        # torno alla seconda pagina
        response = self.client.post(self.url, data=step_1_data)
        self.assertContains(response, step_2_data['start'])
        self.assertContains(response, step_2_data['end'])
        assert_that(response.context['form'].cleaned_data['visibility']).is_true()
        assert_that(response.context['options_form'].cleaned_data['random_order']).is_false()


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

        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.u.id,
            'visibility': Poll.PollVisibility.PUBLIC.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'save': '',
            'code': 'TestCode',
        }

        response = self.client.post(self.url, data=step_2_data)
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse('polls:poll_created_success'))

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
        
        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.u.id,
            'visibility': Poll.PollVisibility.PUBLIC.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'save': '',
            'code': '',
        }

        response = self.client.post(self.url, data=step_2_data)
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse('polls:poll_created_success'))

        #testiamo che sia stato salvato il mapping

        poll_created = Poll.objects.filter(title = 'Lorem ipsum').get()

        #viene creato il mapping
        assert_that(Mapping.objects.filter(poll=poll_created).count()).is_equal_to(1)

        #viene generato un codice alfanumerico lungo 6
        code = Mapping.objects.filter(poll=poll_created).get().code
        result = bool((re.compile("([a-z]|[A-Z]|\d)*")).fullmatch(code)) and (len(code) == 6)
        assert_that(result).is_true()

    
    # test bug 305 (se si torna nella prima pagina e la si modifica, queste modifiche non vengono registrate)
    def test_go_back_and_make_change(self):
        
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
            'summary': ''
        }
        
        step_1_data_modified = {
            'title': 'Test modifica',
            'text': 'testo modificato',
            'default_type': 1,
            'form-TOTAL_FORMS': 3,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
            'form-0-text': 'lorem',
            'form-0-id': '',
            'form-0-DELETE': '',
            'form-1-text': 'ipsum',
            'form-1-id': '',
            'form-1-DELETE': '',
            'form-2-text': 'dolor',
            'form-2-id': '',
            'form-2-DELETE': '',
            'summary': ''
        }

        now = timezone.localtime(timezone.now())
        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'visibility': Poll.PollVisibility.HIDDEN.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'random_order': False,
            'save': ''
        }

        step_2_data_modified = {
            'title': step_1_data_modified['title'],
            'text': step_1_data_modified['text'],
            'default_type': step_1_data_modified['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'visibility': Poll.PollVisibility.HIDDEN.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'random_order': False,
            'save': ''
        }

        response = self.client.post(self.url, data=step_1_data)
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        # torno indietro alla prima pagina
        response = self.client.post(self.url, data=step_2_data | {'go_back': ''})
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        # torno alla seconda pagina
        response = self.client.post(self.url, data=step_1_data_modified)
        assert_that(response.status_code).is_equal_to(200)
        self.assertTemplateUsed('polls/create_poll/summary_and_options_create.html')

        # salvo la scelta
        response = self.client.post(self.url, data=step_2_data_modified | {'save': ''})
        assert_that(response.status_code).is_equal_to(302)
        assert_that(response.url).is_equal_to(reverse('polls:poll_created_success'))

        created_poll = Poll.objects.last()
        assert_that(created_poll.title).is_equal_to('Test modifica')
        assert_that(created_poll.text).is_equal_to('testo modificato')
        alternative_list=[alt[2] for alt in created_poll.alternative_set.all().values_list()]
        assert_that(alternative_list).contains('lorem')
        assert_that(alternative_list).contains('ipsum')
        assert_that(alternative_list).contains('dolor')
        