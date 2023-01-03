from django.test import TestCase
from polls.forms import BaseAlternativeFormSet, PollFormMain, PollFormAdditionalOptions
from assertpy import assert_that  # type: ignore
from polls.models import Poll, Alternative
from django.utils import timezone


class TestBaseAlternativeFormSet(TestCase):
    def setUp(self) -> None:
        p = Poll()
        p.title = "Lorem ipsum"
        p.text = "Dolor sit amet"
        p.start = timezone.now()
        p.end = p.start + timezone.timedelta(weeks=1)
        p.save()
        self.p = p
        p.alternative_set.create(text='Lorem')
        p.alternative_set.create(text='ipsum')
        p.alternative_set.create(text='dolor')

    def test_form_vuoto(self):
        formset = BaseAlternativeFormSet.get_formset_class()(
            queryset=Alternative.objects.none()
        )
        assert_that(formset.total_form_count()).is_equal_to(2)
        assert_that(formset.is_bound).is_false()

    def test_form_precompilato(self):
        formset = BaseAlternativeFormSet.get_formset_class()(
            queryset=self.p.alternative_set.all()
        )
        assert_that(formset.total_form_count()).is_equal_to(3)
        assert_that(formset.is_bound).is_false()

    def test_solo_creazione(self) -> None:
        data = {
            'form-TOTAL_FORMS': 2,
            'form-INITIAL_FORMS': 0,
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
            'form-0-text': 'lorem',
            'form-0-id': '',
            'form-0-DELETE': '',
            'form-1-text': 'ipsum',
            'form-1-id': '',
            'form-1-DELETE': '',
        }
        formset = BaseAlternativeFormSet.get_formset_class()(
            data,
            queryset=Alternative.objects.none()
        )
        assert_that(formset.is_valid()).is_true()
        formset.save(commit=False)
        assert_that(formset.changed_objects).is_length(0)
        assert_that(formset.new_objects).is_length(2)
        assert_that(formset.deleted_objects).is_length(0)
    
    def test_solo_modifica_opzione(self):
        data = {
            'form-TOTAL_FORMS': self.p.alternative_set.count(),
            'form-INITIAL_FORMS': self.p.alternative_set.count(),
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
        }

        for i, alt in enumerate(self.p.alternative_set.all()):
            data = data | {
                f'form-{i}-text': alt.text,
                f'form-{i}-id': alt.id,
                f'form-{i}-DELETE': '',
            }
        data['form-2-text'] = 'sit amet'

        formset = BaseAlternativeFormSet.get_formset_class()(
            data,
            queryset=self.p.alternative_set.all()
        )
        assert_that(formset.is_valid()).is_true()
        formset.save(commit=False)
        assert_that(formset.changed_objects).is_length(1)
        assert_that(formset.new_objects).is_length(0)
        assert_that(formset.deleted_objects).is_length(0)
    
    def test_solo_elimina_opzione(self):
        data = {
            'form-TOTAL_FORMS': self.p.alternative_set.count(),
            'form-INITIAL_FORMS': self.p.alternative_set.count(),
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
        }

        for i, alt in enumerate(self.p.alternative_set.all()):
            data = data | {
                f'form-{i}-text': alt.text,
                f'form-{i}-id': alt.id,
                f'form-{i}-DELETE': '',
            }
        data['form-2-DELETE'] = True

        formset = BaseAlternativeFormSet.get_formset_class()(
            data,
            queryset=self.p.alternative_set.all()
        )
        assert_that(formset.is_valid()).is_true()
        formset.save(commit=False)
        assert_that(formset.changed_objects).is_length(0)
        assert_that(formset.new_objects).is_length(0)
        assert_that(formset.deleted_objects).is_length(1)
    
    def test_combo(self):
        data = {
            'form-TOTAL_FORMS': self.p.alternative_set.count() + 1,
            'form-INITIAL_FORMS': self.p.alternative_set.count(),
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
        }

        for i, alt in enumerate(self.p.alternative_set.all()):
            data = data | {
                f'form-{i}-text': alt.text,
                f'form-{i}-id': alt.id,
                f'form-{i}-DELETE': '',
            }
        data = data | {
            'form-3-text': 'sit amet',
            'form-3-id': '',
            'form-3-DELETE': ''
        }
        data['form-2-DELETE'] = True
        data['form-1-text']= 'consectetur adipiscing elit'

        formset = BaseAlternativeFormSet.get_formset_class()(
            data,
            queryset=self.p.alternative_set.all()
        )
        assert_that(formset.is_valid()).is_true()
        formset.save(commit=False)
        assert_that(formset.changed_objects).is_length(1)
        assert_that(formset.new_objects).is_length(1)
        assert_that(formset.deleted_objects).is_length(1)
    
    def test_crea_da_sessione(self):
        data = {
            'form-TOTAL_FORMS': self.p.alternative_set.count() + 1,
            'form-INITIAL_FORMS': self.p.alternative_set.count(),
            'form-MIN_NUM_FORMS': 2,
            'form-MAX_NUM_FORMS': 10,
        }

        for i, alt in enumerate(self.p.alternative_set.all()):
            data = data | {
                f'form-{i}-text': alt.text,
                f'form-{i}-id': alt.id,
                f'form-{i}-DELETE': '',
            }
        data = data | {
            'form-3-text': '',
            'form-3-id': '',
            'form-3-DELETE': True,
            'form-4-text': 'sit amet',
            'form-4-id': '',
            'form-4-DELETE': ''
        }
        data['form-2-text'] = ''
        data['form-2-DELETE'] = True
        data['form-1-text']= 'consectetur adipiscing elit'
        formset_before: BaseAlternativeFormSet = BaseAlternativeFormSet.get_formset_class()(
            data,
            queryset=self.p.alternative_set.all()
        )
        formset_after = BaseAlternativeFormSet.get_formset_class()(
            formset_before.get_form_for_session(),
            queryset=self.p.alternative_set.all()
        )
        formset_before.save(commit=False)
        formset_after.save(commit=False)
        assert_that(formset_after.new_objects).is_equal_to(formset_before.new_objects)
        assert_that(formset_after.changed_objects).is_equal_to(formset_before.changed_objects)
        assert_that(formset_after.deleted_objects).is_equal_to(formset_before.deleted_objects)

class TestPollFormMain(TestCase):
    def test_errore(self):
        form = PollFormMain({})
        assert_that(form.is_valid()).is_false()
        assert_that(form.errors).is_length(3)
    
    def test_corretto(self):
        form = PollFormMain({'title': 'Lorem', 'text': 'ipsum', 'default_type': 1})
        assert_that(form.is_valid()).is_true()
        p = form.save(commit=False)
        assert_that(p.title).is_equal_to('Lorem')
        assert_that(p.text).is_equal_to('ipsum')
        assert_that(p.default_type).is_equal_to(1)


class TestPollFormAdditionalOptions(TestCase):
    def test_errore(self):
        form = PollFormAdditionalOptions({})
        assert_that(form.is_valid()).is_false()
        assert_that(form.errors).is_length(5)
    
    def test_fine_precedente_inizio(self):
        form = PollFormAdditionalOptions({
            'title': 'Lorem',
            'text': 'ipsum',
            'default_type': 1,
            'start': timezone.now() + timezone.timedelta(days=2),
            'end': timezone.now() + timezone.timedelta(days=1)
        })

        assert_that(form.has_error('end')).is_true()
        assert_that(form.has_error('start')).is_false()
    
    def test_inizio_precedente_5_minuti(self):
        form = PollFormAdditionalOptions({
            'title': 'Lorem',
            'text': 'ipsum',
            'default_type': 1,
            'start': timezone.now() + timezone.timedelta(minutes=4),
            'end': timezone.now() + timezone.timedelta(days=1)
        })

        assert_that(form.has_error('start')).is_true()
        assert_that(form.has_error('end')).is_false()
    
    def test_sondaggio_meno_15_minuti(self):
        form = PollFormAdditionalOptions({
            'title': 'Lorem',
            'text': 'ipsum',
            'default_type': 1,
            'start': timezone.now() + timezone.timedelta(hours=1),
            'end': timezone.now() + timezone.timedelta(hours=1, minutes=14)
        })

        assert_that(form.has_error('end')).is_true()
        assert_that(form.has_error('start')).is_false()
