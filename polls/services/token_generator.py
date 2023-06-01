from __future__ import annotations
from typing import List
from polls.models import TokenizedPoll, Token
import os
import random

#Reads the file containing all the words and loads them in a list
f = open(os.path.normpath('polls/fixtures/word_dictionary.txt'), 'r')
__word_dictionary_list = f.read().split('\n')
f.close()

# Generates n tokens for the given poll
def generate_tokens(poll : TokenizedPoll, n = 0):
    new_tokens_list: List[str] = []
    # Get the list of existing tokens for the given poll
    existing_tokens = list(Token.objects.filter(poll=poll).all().values_list('token', flat=True))
    for _ in range(n):
        # Generate a new token and ensure it is not already in use
        token = __create_token()
        while token in existing_tokens:
            token = __create_token()
        # Add the new token to the lists of tokens
        new_tokens_list.append(token)
        existing_tokens.append(token)
    # Create new Token objects and save them to the database in bulk
    Token.objects.bulk_create([Token(poll=poll, token=t, used=False) for t in new_tokens_list])
    return new_tokens_list


# Create a token by joining four random words from the word dictionary list
def __create_token():
    return ' '.join(random.choices(__word_dictionary_list,k=4))
