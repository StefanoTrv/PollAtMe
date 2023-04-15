from django.test import TestCase
from assertpy import assert_that #type: ignore

from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

from polls.models.mapping import Mapping
from polls.models.poll import Poll, User, TokenizedPoll
from polls.models.token import Token
from polls.models.mapping import Mapping


class TokensViewTest(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username='test1', password='test1')
        self.user2 = User.objects.create_user(username='test2', password='test2')
        now = timezone.localtime(timezone.now())
        self.poll = TokenizedPoll.objects.create(
            title = "Scelta con token",
            text = "Testo della scelta",
            default_type = Poll.PollType.MAJORITY_JUDGMENT,
            author = self.user1,
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
        self.token_page = reverse('polls:tokens', args=[self.poll.pk])


    #test accesso pagina codici, utente non autenticato
    def test_access_token_page_non_authenticated(self):
        response = self.client.get(self.token_page)
        assert_that(response.status_code).is_equal_to(403)

    #test accesso pagina codici, utente autenticato ma diverso dal creatore del sondaggio
    def test_access_token_page_different_users(self):  
        self.client.login(username='test2', password='test2')
        response = self.client.get(self.token_page, args=[self.poll.author])
        assert_that(response.status_code).is_equal_to(403)
    
    #test accesso pagina codici, utente autenticato uguale al creatore del sondaggio
    def test_access_token_page_same_users(self):
        self.client.login(username='test1', password='test1')
        response = self.client.get(self.token_page, args=[self.poll.author])
        assert_that(response.status_code).is_equal_to(200)