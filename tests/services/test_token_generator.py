from datetime import timedelta

from assertpy import assert_that  # type: ignore
from django.contrib.auth.models import User
from django.db.models import Q
from django.test import TestCase
from django.utils import timezone

from polls.models import Poll, TokenizedPoll, Token
from polls.services import generate_tokens
import os


class TestTokenGenerator(TestCase):
    def setUp(self) -> None:
        self.u = User.objects.create_user(username='test')
        poll = {'title': 'C', 'text': 'C', 'start': timezone.now() - timedelta(weeks=1), 'end': timezone.now() + timedelta(weeks=2), 'author': self.u, 'visibility': Poll.PollVisibility.PUBLIC}
        self.poll = TokenizedPoll.objects.create(**poll)
        f = open(os.path.normpath('polls/fixtures/word_dictionary.txt'), 'r')
        self.word_dictionary_list = f.read().split('\n')
        f.close()

    def test_generate_tokens(self):
        tokens = generate_tokens(self.poll,100)
        for token in tokens:
            assert_that(len(token)).is_less_than_or_equal_to(255) # max length of the field in the model is 255
            assert_that(token.split(' ')).is_length(4) # token must be composed of four words
            for word in token.split(' '):
                assert_that(self.word_dictionary_list).contains(word) # each word must be in the dictionary
            assert_that(tokens.count(token)).is_equal_to(1) # every token must be unique
            token_object = Token.objects.filter(token=token).first()
            assert_that(token_object).is_not_none() # the token was created
            assert_that(token_object.poll).is_equal_to(self.poll) # the poll is correct

