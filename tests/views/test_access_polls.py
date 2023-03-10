from django.urls import reverse
from polls.models.alternative import Alternative
from polls.models.mapping import Mapping
from polls.models.poll import Poll, User
from django.test import TestCase
from assertpy import assert_that  # type: ignore


from datetime import timedelta
from django.utils import timezone

#classe per il test dell'accesso ai sondaggi con link breve
class TestAccessPoll(TestCase):

    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test', password='test')
        self.client.login(username='test', password='test')

        self.activePoll = Poll(
            title="Sondaggio attivo", 
            text = "Sondaggio attivo",
            start = timezone.now() - timedelta(weeks=1), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u
        )

        self.activePoll.save()

        Alternative(
            poll = self.activePoll,
            text = "Testo"
        ).save()

        self.waitingPoll = Poll(
            title="Sondaggio in attesa", 
            text = "Sondaggio in attesa",
            start = timezone.now() + timedelta(days=1), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u
        )

        self.waitingPoll.save()

        Alternative(
            poll = self.waitingPoll,
            text = "Testo"
        ).save()

        self.endedPoll = Poll(
            title="Sondaggio attivo", 
            text = "Sondaggio attivo",
            start = timezone.now() - timedelta(weeks=1), 
            end = timezone.now() - timedelta(days=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u
        )

        self.endedPoll.save()

        Alternative(
            poll = self.endedPoll,
            text = "Testo"
        ).save()

        self.activePollCode = "activePoll"
        self.waitingPollCode = "waitingPoll"
        self.endedPollCode = "endedPoll"

        Mapping(
            poll = self.activePoll,
            code = self.activePollCode,
        ).save()
        
        Mapping(
            poll = self.waitingPoll,
            code = self.waitingPollCode,
        ).save()

        Mapping(
            poll = self.endedPoll,
            code = self.endedPollCode,
        ).save()

    def test_access_active_poll(self):
        response = self.client.get(reverse('polls:access_poll', kwargs={'code': self.activePollCode}))
        assert_that(response['Location']).is_equal_to(reverse('polls:vote', kwargs={'id': self.activePoll.pk}))

    def test_access_waiting_poll(self):
        response = self.client.get(reverse('polls:access_poll', kwargs={'code': self.waitingPollCode})) #primo redirect
        response = self.client.get(response['Location']) #secondo redirect
        response = self.client.get(response['Location']) #pagina di voto
        assert_that(response.status_code).is_equal_to(403)

    def test_access_ended_poll(self):
        response = self.client.get(reverse('polls:access_poll', kwargs={'code': self.endedPollCode}))
        assert_that(response['Location']).is_equal_to(reverse('polls:result', kwargs={'id': self.endedPoll.pk}))