from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from polls.models import Alternative, Poll, SinglePreference, PollOptions, Mapping

from django.db import IntegrityError

class Modeltest(TestCase):

    poll_title = "Età"
    poll_text = "Quanti anni hai?"

    def setUp(self):
        self.u = User.objects.create_user(username='test')
        poll = Poll(
            title=self.poll_title, 
            text=self.poll_text,
            default_type=Poll.PollType.SINGLE_PREFERENCE,
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1),
            author=self.u
            )
        poll.save()
        alternative1 = Alternative(poll = poll, text = "32")
        alternative1.save()
        alternative2 = Alternative(poll = poll, text = "50")
        alternative2.save()
        preference1 = SinglePreference(poll = poll, alternative = alternative1)
        preference1.save()

    def test_poll(self):
        poll = Poll.objects.get(title=self.poll_title)
        self.assertEqual(poll.title, self.poll_title)
        self.assertEqual(poll.text, self.poll_text)

    def test_poll_is_active(self):
        poll = Poll()
        poll.start = timezone.now()
        poll.end = timezone.now() + timedelta(weeks=1)

        self.assertTrue(poll.is_active())
        self.assertFalse(poll.is_ended())
        self.assertFalse(poll.is_not_started())

    def test_poll_is_ended(self):
        poll = Poll()
        poll.start = timezone.now() - timedelta(weeks=2)
        poll.end = timezone.now() - timedelta(weeks=1)

        self.assertFalse(poll.is_active())
        self.assertTrue(poll.is_ended())
        self.assertFalse(poll.is_not_started())
    
    def test_poll_not_started(self):
        poll = Poll()
        poll.start = timezone.now() + timedelta(weeks=1)
        poll.end = timezone.now() + timedelta(weeks=2)

        self.assertFalse(poll.is_active())
        self.assertFalse(poll.is_ended())
        self.assertTrue(poll.is_not_started())

    
    def test_poll_type_preferenza_singola(self):
        poll = Poll(
            title=self.poll_title, 
            text=self.poll_text,
            default_type=Poll.PollType.SINGLE_PREFERENCE,
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1),
            author=self.u)
        poll.save()

        self.assertEqual(poll.get_type(), 'Preferenza singola')
    
    def test_poll_type_giudizio_maggioritario(self):
        poll = Poll(
            title=self.poll_title, 
            text=self.poll_text,
            default_type=Poll.PollType.MAJORITY_JUDGMENT,
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1),
            author=self.u)
        poll.save()
        
        self.assertEqual(poll.get_type(), 'Giudizio maggioritario')

    def test_poll_type_shultze_method(self):
        poll = Poll(
            title=self.poll_title, 
            text=self.poll_text,
            default_type=Poll.PollType.SHULTZE_METHOD,
            start=timezone.now() - timedelta(weeks=1), 
            end=timezone.now() + timedelta(weeks=1),
            author=self.u)
        poll.save()
        
        self.assertEqual(poll.get_type(), 'Metodo Schulze')

    def test_choice_fk(self):
        poll = Poll.objects.get(text=self.poll_text)
        alternative = Alternative.objects.get(poll = poll, text="32")
        self.assertEqual(alternative.poll.id, poll.id)
    
    def test_choice(self):
        a1 = Alternative.objects.get(text='32')
        self.assertEqual(a1.text,'32')
    
    #Controllo che due alternative puntino a una stessa domanda
    def test_choice_samefk(self):
        a1 = Alternative.objects.get(text='50')
        a2 = Alternative.objects.get(text='32')
        self.assertEqual(a1.poll.id, a2.poll.id)

    #Controllo che il voto leghi una opzione e una domanda
    def test_vote_samefk(self):
        q1 = Poll.objects.get(title=self.poll_title)
        a1 = Alternative.objects.get(text='32')
        p1 = SinglePreference.objects.get(poll = q1, alternative = a1)
        self.assertEqual(p1.poll.id, q1.id)
        self.assertEqual(p1.alternative.id, a1.id)

class TestPollMapping(TestCase):
    def setUp(self) -> None:
        self.p = Poll()
        self.p.title = "Test"
        self.p.text = "Test"
        self.p.author = User.objects.create_user(username='test')
        self.p.start = timezone.now()
        self.p.end = timezone.now() + timedelta(weeks=1)
        self.p.default_type = Poll.PollType.SINGLE_PREFERENCE
        self.p.save()
    
    def test_mapping_save(self):
        mapping = Mapping(poll=self.p, code="Test")
        mapping.save()

        self.assertEqual(mapping.poll, self.p)
        self.assertEqual(mapping.code, "Test")

    def test_one_to_one(self):
        mapping = Mapping(poll=self.p, code="Test")
        mapping.save()

        self.assertRaises(IntegrityError, Mapping.objects.create, poll=self.p, code="Test1")       

    def test_unique(self):
        new_p = Poll.objects.first()
        new_p.pk = None
        new_p.save()

        mapping = Mapping(poll=self.p, code="Test")
        mapping.save()

        self.assertRaises(IntegrityError, Mapping.objects.create, poll=new_p, code="Test")


class TestPollOptions(TestCase):
    def setUp(self) -> None:
        self.p = Poll()
        self.p.title = "Test"
        self.p.text = "Test"
        self.p.author = User.objects.create_user(username='test')
        self.p.start = timezone.now()
        self.p.end = timezone.now() + timedelta(weeks=1)
        self.p.default_type = Poll.PollType.SINGLE_PREFERENCE
        self.p.save()

    def test_default_fields(self):
        options = PollOptions(poll=self.p)
        options.save()

        self.assertEqual(options.poll, self.p)
        self.assertEqual(self.p.polloptions, options)
        
        self.assertTrue(options.random_order)
    
    def test_random_order_flag(self):
        options = PollOptions(poll=self.p, random_order=False)
        options.save()

        self.assertFalse(options.random_order)

        options.random_order = True
        options.save()

        self.assertTrue(options.random_order)