from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from assertpy import assert_that  # type: ignore

from polls.models import Poll, Mapping, Token, TokenizedPoll, PollOptions, MajorityPreference, MajorityOpinionJudgement

class TestTokenizedPollsCreate(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')
        now = timezone.localtime(timezone.now())
        self.poll = TokenizedPoll.objects.create(
            title = "Scelta con token",
            text = "Testo della scelta",
            default_type = Poll.PollType.MAJORITY_JUDGMENT,
            author = self.u,
            start = now - timedelta(minutes=20),
            end = now + timedelta(weeks=1),
            creation_date = now,
            last_update = now,
            visibility = Poll.PollVisibility.PUBLIC,
            authentication_type = Poll.PollAuthenticationType.TOKENIZED,
        )
        self.token = Token.objects.create(poll=self.poll,token="abcdef")
        self.poll.alternative_set.create(text='prima scelta')
        self.poll.alternative_set.create(text='seconda scelta')
        self.mapping = Mapping.objects.create(poll=self.poll,code="code")
        self.poll_url = reverse('polls:vote_MJ', args=[self.poll.pk,self.token.token])

    # Crea un sondaggio con token
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
            'visibility': Poll.PollVisibility.PUBLIC.value,
            'authentication_type': Poll.PollAuthenticationType.TOKENIZED.value,
            'save': ''
        }
        response = self.client.post(reverse('polls:create_poll'), data=step_2_data)
        assert_that(response.status_code).is_equal_to(200)

        try:
            p = Poll.objects.get(title='Lorem ipsum')
        except Poll.DoesNotExist:
            self.fail('Poll was not created')
        assert_that(p.authentication_type).is_equal_to(Poll.PollAuthenticationType.TOKENIZED.value)

        try:
            ap = TokenizedPoll.objects.get(title='Lorem ipsum')
        except TokenizedPoll.DoesNotExist:
            self.fail('Tokenized Poll was not created')
        assert_that(ap.poll_ptr).is_equal_to(p)

    def test_edit_tokenized_poll(self):
        self.client.login(username='test', password='test')
        tp = TokenizedPoll()
        tp.title = 'Lorem ipsum'
        tp.text = 'dolor sit amet'
        tp.default_type = Poll.PollType.SINGLE_PREFERENCE
        tp.author = self.u
        tp.start = timezone.localtime(timezone.now()) + timedelta(minutes=20)
        tp.end = timezone.localtime(timezone.now()) + timedelta(weeks=1)
        tp.visibility = Poll.PollVisibility.HIDDEN
        tp.authentication_type = Poll.PollAuthenticationType.TOKENIZED
        tp.mapping = Mapping(code="loremipsum")
        tp.polloptions = PollOptions()
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
            'visibility': Poll.PollVisibility.PUBLIC.value,
            'authentication_type': Poll.PollAuthenticationType.FREE.value,
            'save': ''
        }

        response = self.client.post(reverse('polls:edit_poll', args=[tp.pk]), data=step_1_data)
        assert_that(response.status_code).is_equal_to(200)
        response = self.client.post(reverse('polls:edit_poll', args=[tp.pk]), data=step_2_data)
        self.assertContains(response, 'Fatto! La tua scelta è stata modificata.')

        tp = Poll.objects.get(id=tp.pk)
        assert_that(tp.authentication_type).is_equal_to(Poll.PollAuthenticationType.FREE.value)
        assert_that(getattr).raises(AttributeError).when_called_with(tp, Poll.TOKEN_VOTE_TYPE_FIELDNAME)
    
    #test accesso alla pagina di voto
    def test_reach_vote_page(self):
        response = self.client.get(self.poll_url)
        self.assertContains(response, "Testo della scelta")
    
    #test di voto
    def test_vote_with_token(self):
        last_vote_old = MajorityPreference.objects.last()
        resp = self.client.post(self.poll_url, {
            'majorityopinionjudgement_set-TOTAL_FORMS': 2,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 2,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 2,
            'majorityopinionjudgement_set-0-grade': 1,
            'majorityopinionjudgement_set-1-grade': 1,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(
            response=resp,
            template_name='polls/vote_success.html'
        )

        last_vote = MajorityPreference.objects.last()
        assert_that(last_vote).is_not_equal_to(last_vote_old)

        for judgement in last_vote.majorityopinionjudgement_set.all():
            self.assertEqual(judgement.grade, 1)
    
    #test blocco voto se il token è errato (sia accesso alla pagina che salvataggio del voto)
    def test_wrong_token(self):
        response = self.client.get(reverse('polls:vote_MJ', args=[self.poll.pk,"token_errato"]))
        assert_that(response.status_code).is_equal_to(403)

        last_vote_old = MajorityPreference.objects.last()
        resp = self.client.post(reverse('polls:vote_MJ', args=[self.poll.pk,"token_errato"]), {
            'majorityopinionjudgement_set-TOTAL_FORMS': 2,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 2,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 2,
            'majorityopinionjudgement_set-0-grade': 1,
            'majorityopinionjudgement_set-1-grade': 1,
        })
        self.assertEqual(resp.status_code, 403)
        last_vote = MajorityPreference.objects.last()
        assert_that(last_vote).is_equal_to(last_vote_old)
    
    #test redirect se token già usato
    def test_redirect_on_used_token(self):
        self.token.used=True
        self.token.save()
        response = self.client.get(self.poll_url,follow=True)
        self.assertRedirects(response,reverse('polls:result_MJ',args=[self.poll.pk]))

    def test_does_not_save_on_used_token(self):
        self.token.used=True
        self.token.save()
        last_vote_old = MajorityPreference.objects.last()
        resp = self.client.post(reverse('polls:vote_MJ', args=[self.poll.pk,"token_errato"]), {
            'majorityopinionjudgement_set-TOTAL_FORMS': 2,
            'majorityopinionjudgement_set-INITIAL_FORMS': 0,
            'majorityopinionjudgement_set-MIN_NUM_FORMS': 2,
            'majorityopinionjudgement_set-MAX_NUM_FORMS': 2,
            'majorityopinionjudgement_set-0-grade': 1,
            'majorityopinionjudgement_set-1-grade': 1,
        })
        #self.assertEqual(resp.status_code, 403)
        last_vote = MajorityPreference.objects.last()
        assert_that(last_vote).is_equal_to(last_vote_old)

    #test redirect da url abbreviato a pagina di voto
    def test_redirect_from_short_url(self):
        response = self.client.get(reverse('polls:access_poll', args=[self.poll.mapping.code,self.token.token]),follow=True)
        self.assertRedirects(response,self.poll_url)