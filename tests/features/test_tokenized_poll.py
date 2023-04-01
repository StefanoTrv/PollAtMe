from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from assertpy import assert_that  # type: ignore

from polls import models

class TestTokenizedPollsCreate(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')

    # Crea un sondaggio autenticato
    def test_create_tokenized_poll(self):
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
            'summary': ''
        }
        response = self.client.post(
            reverse('polls:create_poll'), data=step_1_data)
        now = timezone.localtime(timezone.now())

        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': (now + timedelta(minutes=20)).strftime('%Y-%m-%d %H:%M:%S'),
            'end': (now + timedelta(weeks=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'visibility': models.Poll.PollVisibility.PUBLIC.value,
            'authentication_type': models.Poll.PollAuthenticationType.TOKENIZED.value,
            'save': ''
        }
        response = self.client.post(reverse('polls:create_poll'), data=step_2_data)
        assert_that(response.status_code).is_equal_to(200)

        try:
            p = models.Poll.objects.get(title='Lorem ipsum')
        except models.Poll.DoesNotExist:
            self.fail('Poll was not created')
        assert_that(p.authentication_type).is_equal_to(models.Poll.PollAuthenticationType.TOKENIZED.value)

        try:
            ap = models.TokenizedPoll.objects.get(title='Lorem ipsum')
        except models.TokenizedPoll.DoesNotExist:
            self.fail('Tokenized Poll was not created')
        assert_that(ap.poll_ptr).is_equal_to(p)

    def test_edit_tokenized_poll(self):
        self.client.login(username='test', password='test')
        tp = models.TokenizedPoll()
        tp.title = 'Lorem ipsum'
        tp.text = 'dolor sit amet'
        tp.default_type = models.Poll.PollType.SINGLE_PREFERENCE
        tp.author = self.u
        tp.start = timezone.localtime(timezone.now()) + timedelta(minutes=20)
        tp.end = timezone.localtime(timezone.now()) + timedelta(weeks=1)
        tp.visibility = models.Poll.PollVisibility.HIDDEN
        tp.authentication_type = models.Poll.PollAuthenticationType.TOKENIZED
        tp.mapping = models.Mapping(code="loremipsum")
        tp.polloptions = models.PollOptions()
        tp.save()
        tp.mapping.save()
        tp.polloptions.save()

        tp.alternative_set.create(text='lorem')
        tp.alternative_set.create(text='ipsum')

        step_1_data = {
            'title': tp.title,
            'text': tp.text,
            'default_type': tp.default_type,
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

        step_2_data = {
            'title': step_1_data['title'],
            'text': step_1_data['text'],
            'default_type': step_1_data['default_type'],
            'start': tp.start.strftime('%Y-%m-%d %H:%M:%S'),
            'end': tp.end.strftime('%Y-%m-%d %H:%M:%S'),
            'visibility': models.Poll.PollVisibility.PUBLIC.value,
            'authentication_type': models.Poll.PollAuthenticationType.FREE.value,
            'save': ''
        }

        response = self.client.post(reverse('polls:edit_poll', args=[tp.pk]), data=step_1_data)
        assert_that(response.status_code).is_equal_to(200)
        response = self.client.post(reverse('polls:edit_poll', args=[tp.pk]), data=step_2_data)
        self.assertContains(response, 'Fatto! La tua scelta è stata modificata.')

        tp = models.Poll.objects.get(id=tp.pk)
        assert_that(tp.authentication_type).is_equal_to(models.Poll.PollAuthenticationType.FREE.value)
        assert_that(getattr).raises(AttributeError).when_called_with(tp, models.Poll.TOKEN_VOTE_TYPE_FIELDNAME)