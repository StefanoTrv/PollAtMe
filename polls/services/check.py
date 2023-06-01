from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from django.core.exceptions import PermissionDenied
from django.utils import timezone

from polls.models import Poll, Preference, Token


class Handler(ABC):
    """Chain responsibility rule for ownership, state, etc. checks of a poll"""

    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, **kwargs):
        pass

class AbstractHandler(Handler):
    
    _next_handler: Optional[Handler] = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self):
        if self._next_handler:
            return self._next_handler.handle()
        return None

class CheckPollActiveness(AbstractHandler):
    """Checks if poll is active. If not, a 403 exception is raised"""

    def __init__(self, poll: Poll) -> None:
        self.poll = poll
        super().__init__()

    def handle(self):
        if not self.poll.is_active():
            start = timezone.localtime(self.poll.start)
            if timezone.now() < start:
                raise PermissionDenied(f'Le votazioni inizieranno il {start.strftime("%d/%m/%Y")} alle {start.strftime("%H:%M")}')
            else:
                end = timezone.localtime(self.poll.end)
                raise PermissionDenied(f'La scelta è terminata il {end.strftime("%d/%m/%Y")} alle {end.strftime("%H:%M")}')
        
        return super().handle()

class CheckPollIsNotStarted(AbstractHandler):

    def __init__(self, poll: Poll) -> None:
        self.poll = poll
        super().__init__()
    
    def handle(self):
        if not self.poll.is_not_started():
            raise PermissionDenied('Non è possibile effettuare questa operazione dopo che la votazione è iniziata')
        
        return super().handle()

class CheckPollIsNotEnded(AbstractHandler):
    
        def __init__(self, poll: Poll) -> None:
            self.poll = poll
            super().__init__()
        
        def handle(self):
            if self.poll.is_ended():
                raise PermissionDenied('Non è possibile effettuare questa operazione dopo che la votazione è terminata')
            
            return super().handle()

class CheckAuthentication(AbstractHandler):
    """
    Checks if the user is authenticated. If not, the failed_authentication function,
    which is passed as a parameter, is executed
    """

    def __init__(self, poll: Poll, is_authenticated: bool, token, failed_authentication) -> None:
        self.poll = poll
        self.is_authenticated = is_authenticated
        self.token = token
        self.failed_authentication = failed_authentication
        super().__init__()

    def handle(self):
        if self.poll.failed_authentication(user=self.is_authenticated, token=self.token):
            return self.failed_authentication()
        
        return super().handle()

class CheckUserHasVoted(AbstractHandler):
    """
    Checks if the user has already voted. If yes, the has_voted function,  
    which is passed as a parameter, is executed
    """

    def __init__(self, poll: Poll, user, token, syntethic_preference, has_voted) -> None:
        self.poll = poll
        self.user = user
        self.token = token
        self.syntethic_preference = syntethic_preference
        self.has_voted = has_voted
        super().__init__()

    def handle(self, **kwargs):
        if self.poll.user_has_already_voted(user=self.user, token=self.token) and self.syntethic_preference is None:
            return self.has_voted()
        
        return super().handle()

class CheckRevoteSession(AbstractHandler):
    """Checks if the user is revoting and the correctness of the data in session"""

    def __init__(self, poll: Poll, session_vote_type, is_preference_in_session, syntethic_preference: Preference) -> None:
        self.poll = poll
        self.session_vote_type = session_vote_type
        self.is_preference_in_session = is_preference_in_session
        self.syntethic_preference = syntethic_preference
        super().__init__()
    
    def handle(self):
        if not (self.poll.get_type() == self.session_vote_type or self.is_preference_in_session):
            raise PermissionDenied(
                'Il voto con metodi alternativi è concesso solo durante il rivoto')
        
        if not (self.syntethic_preference is None or self.syntethic_preference.poll.pk == self.poll.pk):
            raise PermissionDenied(
                '''Il voto con metodi alternativi è concesso solo durante il rivoto
                (Dettagli dell'errore: la preferenza sintetica è riferita ad una scelta diversa)'''
            )

        return super().handle()

class CheckPollOwnership(AbstractHandler):

    def __init__(self, poll: Poll, user) -> None:
        self.poll = poll
        self.user = user
        super().__init__()
    
    def handle(self):
        if self.poll.author != self.user:
            raise PermissionDenied('Non hai i permessi per cancellare questa scelta')
        
        return super().handle()

class CheckPollAuthenticationType(AbstractHandler):
    def __init__(self, poll: Poll, vote_type: type) -> None:
        self.poll = poll
        self.vote_type = vote_type
        super().__init__()
    
    def handle(self):
        if not isinstance(self.poll, self.vote_type):
            raise PermissionDenied('Non è possibile effettuare questa operazione con questo metodo di voto')
        
        return super().handle()

class CheckTokenNotUsed(AbstractHandler):
    """Checks if the token has been used. If yes, it raises a PermissionDenied exception"""
    
    def __init__(self, token: Token, msg: str) -> None:
        self.token = token
        self.msg = msg
        super().__init__()
    
    def handle(self):
        if self.token.used:
            raise PermissionDenied(self.msg)
        
        return super().handle()