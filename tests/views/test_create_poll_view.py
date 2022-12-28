import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from assertpy import assert_that  # type: ignore

from polls.models import SinglePreferencePoll, MajorityOpinionPoll

class CreatePollViewTest(TestCase):
    
    url = reverse('polls:create_poll')
    data={
            'poll_title': 'titolo',
            'poll_type': 'Giudizio maggioritario',
            'poll_text': 'testo della domanda',
            'hidden_alternative_count': '3',
            'alternative1': 'prima alternativa',
            'alternative2': 'seconda alternativa', 
            'alternative3': 'terza alternativa'
        }

    def test_aggiunta_poll_preferenza_singola(self):
        start_time=timezone.now()
        end_time=timezone.now()+datetime.timedelta(weeks=1)
        data=self.data.copy()
        data['poll_type']='Preferenza singola'

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, data['alternative3'])
        response = self.client.post(self.url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Perfetto! Il tuo sondaggio è stato creato.')
        last_poll = SinglePreferencePoll.objects.last()
        self.assertIsNotNone(last_poll)
        self.assertEqual(last_poll.title,data['poll_title'])
        self.assertEqual(last_poll.text,data['poll_text'])
        self.assertEqual(len(last_poll.alternative_set.all()),3)
        assert_that(last_poll.start).is_equal_to(start_time)
        assert_that(last_poll.end).is_equal_to(end_time)
        alternatives = [data['alternative1'], data['alternative2'], data['alternative3']]
        for alternative in last_poll.alternative_set.all():
            self.assertIn(alternative.text,alternatives)

    def test_aggiunta_poll_giudizio_maggioritario(self):
        start_time=timezone.now()
        end_time=timezone.now()+datetime.timedelta(weeks=1)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.data['alternative3'])
        response = self.client.post(self.url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,'Perfetto! Il tuo sondaggio è stato creato.')
        last_poll = MajorityOpinionPoll.objects.last()
        self.assertIsNotNone(last_poll)
        self.assertEqual(last_poll.title,self.data['poll_title'])
        self.assertEqual(last_poll.text,self.data['poll_text'])
        self.assertEqual(len(last_poll.alternative_set.all()),3)
        assert_that(last_poll.start).is_equal_to(start_time)
        assert_that(last_poll.end).is_equal_to(end_time)
        alternatives = [self.data['alternative1'], self.data['alternative2'], self.data['alternative3']]
        for alternative in last_poll.alternative_set.all():
            self.assertIn(alternative.text,alternatives)
    
    

    def test_stop_if_not_enough_alternatives(self):
        data=self.data.copy()
        del data['alternative2']
        del data['alternative3']

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il numero di alternative deve essere compreso tra 2 e 10.')#controllo il messaggio di errore
        
    def test_stop_if_whitespace_only_title(self):
        data=self.data.copy()
        data['poll_title']='   '

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il titolo non può essere vuoto.')#controllo il messaggio di errore

    def test_stop_if_whitespace_only_text(self):
        data=self.data.copy()
        data['poll_text']='   '

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il testo del sondaggio non può essere vuoto.')#controllo il messaggio di errore
    
    def test_stop_if_vote_starts_before_now(self):
        self.client.post(self.url, self.data)
        self.client.get(self.url)

        start_time=timezone.now()-datetime.timedelta(days=1)
        end_time=timezone.now()+datetime.timedelta(weeks=1)

        response = self.client.post(self.url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il momento di inizio delle votazioni deve essere successivo ad adesso.')#controllo il messaggio di errore
    
    def test_stop_if_vote_ends_too_early(self):
        self.client.post(self.url, self.data)
        self.client.get(self.url)

        start_time=timezone.now()
        end_time=timezone.now()+datetime.timedelta(minutes=2)

        response = self.client.post(self.url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il momento di fine delle votazioni deve essere almeno cinque minuti da adesso.')#controllo il messaggio di errore
    
    def test_stop_if_vote_ends_before_starting(self):
        self.client.post(self.url, self.data)
        self.client.get(self.url)

        start_time=timezone.now()+datetime.timedelta(days=2)
        end_time=timezone.now()+datetime.timedelta(days=1)

        response = self.client.post(self.url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il momento di fine delle votazioni deve essere successivo a quello di inizio.')#controllo il messaggio di errore
    
    def test_stop_if_vote_time_too_short(self):
        self.client.post(self.url, self.data)
        self.client.get(self.url)

        start_time=timezone.now()+datetime.timedelta(days=1)
        end_time=timezone.now()+datetime.timedelta(days=1)+datetime.timedelta(minutes=2)

        response = self.client.post(self.url, data={
            'start_time': start_time,
            'end_time': end_time
        })
        self.assertEqual(response.status_code, 200)#resta nella stessa pagina
        self.assertContains(response,'Il momento di fine delle votazioni deve essere almeno cinque minuti dopo quello di inizio.')#controllo il messaggio di errore
        


