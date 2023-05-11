from assertpy import assert_that # type: ignore
from django.test import TestCase
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.contrib.auth.models import User

from polls import models
from polls.services import check

class TestCheckPollActiveness(TestCase):

    def test_check_active_poll(self):
        poll = models.Poll()
        poll.start = timezone.now() + timezone.timedelta(days=1)

        handler = check.CheckPollActiveness(poll)
        assert_that(handler.handle).raises(PermissionDenied).when_called_with()

    def test_check_poll_is_active(self):
        poll = models.Poll()
        poll.start = timezone.now() - timezone.timedelta(days=1)
        poll.end = poll.start + timezone.timedelta(days=2)

        handler = check.CheckPollActiveness(poll)
        assert_that(handler.handle()).is_none()

class TestCheckPollIsNotStarted(TestCase):
    def test_check_poll_started(self):
        poll = models.Poll()
        poll.start = timezone.now() - timezone.timedelta(days=1)

        handler = check.CheckPollIsNotStarted(poll)
        assert_that(handler.handle).raises(PermissionDenied).when_called_with()

    def test_check_poll_not_started(self):
        poll = models.Poll()
        poll.start = timezone.now() + timezone.timedelta(days=1)

        handler = check.CheckPollIsNotStarted(poll)
        assert_that(handler.handle()).is_none()

class TestCheckPollIsNotEnded(TestCase):
    def test_check_poll_ended(self):
        poll = models.Poll()
        poll.end = timezone.now() - timezone.timedelta(days=1)

        handler = check.CheckPollIsNotEnded(poll)
        assert_that(handler.handle).raises(PermissionDenied).when_called_with()

    def test_check_poll_not_ended(self):
        poll = models.Poll()
        poll.end = timezone.now() + timezone.timedelta(days=1)

        handler = check.CheckPollIsNotEnded(poll)
        assert_that(handler.handle()).is_none()

class TestCheckAuthentication(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')

    def test_free_poll(self):
        poll = models.Poll()

        handler = check.CheckAuthentication(poll, True, None, lambda: False)
        assert_that(handler.handle()).is_none()
    
    def test_authenticated_poll_with_authenticated_user(self):
        poll = models.AuthenticatedPoll()

        handler = check.CheckAuthentication(poll, True, None, lambda: False)
        assert_that(handler.handle()).is_none()
    
    def test_authenticated_poll_with_anonymous_user(self):
        poll = models.AuthenticatedPoll()

        handler = check.CheckAuthentication(poll, False, None, lambda: False)
        assert_that(handler.handle()).is_false()

    def test_tokenized_poll_with_valid_token(self):
        poll = models.TokenizedPoll.objects.create(
            author = self.user,
            title = "test",
            start = timezone.now() - timezone.timedelta(days=1),
            end = timezone.now() + timezone.timedelta(days=1)
        )
        token = models.Token.objects.create(
            poll=poll,
            token="test test test test",
            used=False
        )

        handler = check.CheckAuthentication(poll, False, token.token, lambda: False)
        assert_that(handler.handle()).is_none()

    def test_tokenized_poll_with_invalid_token(self):
        poll = models.TokenizedPoll.objects.create(
            author = self.user,
            title = "test",
            start = timezone.now() - timezone.timedelta(days=1),
            end = timezone.now() + timezone.timedelta(days=1)
        )

        handler = check.CheckAuthentication(poll, False, "invalid token", lambda: False)
        assert_that(handler.handle()).is_false()

class TestCheckUserHasVoted(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')

    def test_free_poll(self):
        poll = models.Poll()

        handler = check.CheckUserHasVoted(poll, self.user, None, None, lambda: False)
        assert_that(handler.handle()).is_none()

class TestCheckRevoteSession(TestCase):
    def test_check_revote(self):
        pass

class TestCheckPollOwnership(TestCase):
    def test_poll_ownership(self):
        pass

class TestCheckPollAuthenticationType(TestCase):
    def test_poll_authentication_type(self):
        pass

class TestCheckTokenNotUsed(TestCase):
    def test_token_not_used(self):
        pass

