from __future__ import annotations
from typing import List
from polls.models import TokenizedPoll, Token
import os
import random

#Reads the file containing all the words and loads them in a list
f = open(os.path.normpath('polls/fixtures/word_dictionary.txt'), 'r')
__word_dictionary_list = f.read().split('\n')
f.close()

def generate_tokens(poll : TokenizedPoll, n = 0):
    new_tokens_list: List[str] = []
    for i in range(n):
        token = __create_token()
        while Token.objects.filter(token=token).filter(poll=poll).count() != 0:
            token = __create_token()
        Token.objects.create(poll=poll, token=token, used=False)
        new_tokens_list.append(token)
    return new_tokens_list

def __create_token():
    return ' '.join(random.choices(__word_dictionary_list,k=4))
