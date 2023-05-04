from assertpy import assert_that  # type: ignore
from django.test import TestCase
from polls.models import Poll
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import User


class TestResultsVisibilityMJ(TestCase):

    def setUp(self):
        self.u = User.objects.create_user(username='test', password='test')
        self.u1 = User.objects.create_user(username='test1', password='test1')
        self.poll1 = Poll(
            title="Tutti possono vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.ALL
        )
        self.poll1.save()
        self.a1 = self.poll1.alternative_set.create(text="Risposta 1")
        self.poll2 = Poll(
            title="Solo il creatore può vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.AUTHOR
        )
        self.poll2.save()
        self.a1 = self.poll2.alternative_set.create(text="Risposta 1")
        self.poll3 = Poll(
            title="Nessuno può vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.NOBODY
        )
        self.poll3.save()
        self.a1 = self.poll3.alternative_set.create(text="Risposta 1")

    def test_show_results_all_to_creator(self):
        url = reverse('polls:result_MJ', args=[self.poll1.pk])
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll1.results_restriction)+'-show')

    def test_show_results_all_to_someone_else(self):
        url = reverse('polls:result_MJ', args=[self.poll1.pk])
        self.client.login(username="test1", password="test1")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll1.results_restriction)+'-show')

    def test_show_results_only_creator_to_creator(self):
        url = reverse('polls:result_MJ', args=[self.poll2.pk])
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll2.results_restriction)+'-show')

    def test_show_results_only_creator_to_someone_else(self):
        url = reverse('polls:result_MJ', args=[self.poll2.pk])
        self.client.login(username="test1", password="test1")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll2.results_restriction)+'-lock')

    def test_show_results_nobody_to_creator(self):
        url = reverse('polls:result_MJ', args=[self.poll3.pk])
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll3.results_restriction)+'-lock')

    def test_show_results_nobody_to_someone_else(self):
        url = reverse('polls:result_MJ', args=[self.poll3.pk])
        self.client.login(username="test1", password="test1")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll3.results_restriction)+'-lock')



class TestResultsVisibilitySP(TestCase):

    def setUp(self):
        self.u = User.objects.create_user(username='test', password='test')
        self.u1 = User.objects.create_user(username='test1', password='test1')
        self.poll1 = Poll(
            title="Tutti possono vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            default_type = Poll.PollType.SINGLE_PREFERENCE,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.ALL
        )
        self.poll1.save()
        self.a1 = self.poll1.alternative_set.create(text="Risposta 1")
        self.a2 = self.poll1.alternative_set.create(text="Risposta 2")
        self.poll2 = Poll(
            title="Solo il creatore può vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            default_type = Poll.PollType.SINGLE_PREFERENCE,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.AUTHOR
        )
        self.poll2.save()
        self.a1 = self.poll2.alternative_set.create(text="Risposta 1")
        self.a2 = self.poll2.alternative_set.create(text="Risposta 2")
        self.poll3 = Poll(
            title="Nessuno può vedere i risultati", 
            text = "Sondaggio di prova",
            start = timezone.now(), 
            end = timezone.now() + timedelta(weeks=1),
            visibility = Poll.PollVisibility.PUBLIC,
            default_type = Poll.PollType.SINGLE_PREFERENCE,
            author=self.u,
            results_restriction = Poll.PollResultsRestriction.NOBODY
        )
        self.poll3.save()
        self.a1 = self.poll3.alternative_set.create(text="Risposta 1")
        self.a2 = self.poll3.alternative_set.create(text="Risposta 2")

    def test_show_results_all_to_creator(self):
        url = reverse('polls:result_single_preference', args=[self.poll1.pk])
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll1.results_restriction)+'-show')

    def test_show_results_all_to_someone_else(self):
        url = reverse('polls:result_single_preference', args=[self.poll1.pk])
        self.client.login(username="test1", password="test1")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll1.results_restriction)+'-show')

    def test_show_results_only_creator_to_creator(self):
        url = reverse('polls:result_single_preference', args=[self.poll2.pk])
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll2.results_restriction)+'-show')

    def test_show_results_only_creator_to_someone_else(self):
        url = reverse('polls:result_single_preference', args=[self.poll2.pk])
        self.client.login(username="test1", password="test1")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll2.results_restriction)+'-lock')

    def test_show_results_nobody_to_creator(self):
        url = reverse('polls:result_single_preference', args=[self.poll3.pk])
        self.client.login(username="test", password="test")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll3.results_restriction)+'-lock')

    def test_show_results_nobody_to_someone_else(self):
        url = reverse('polls:result_single_preference', args=[self.poll3.pk])
        self.client.login(username="test1", password="test1")
        response = self.client.get(url)
        self.assertContains(response, str(self.poll3.results_restriction)+'-lock')

    