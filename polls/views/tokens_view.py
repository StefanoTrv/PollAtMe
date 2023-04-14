
from django import http
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.generic import FormView, ListView, DeleteView

from polls.forms import TokenGeneratorForm
from polls.models import Token, TokenizedPoll, Poll
from polls.services import SearchPollService, TicketGenerator
from polls.services.token_generator import generate_tokens
from django.urls import reverse


class TokensView(LoginRequiredMixin, FormView, ListView):
    template_name = 'polls/tokens_page.html'
    form_class = TokenGeneratorForm
    paginate_by = 9

    def dispatch(self, request, *args, **kwargs):
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        self.tokens = Token.objects.filter(poll = self.poll)

        if self.poll.author != request.user:
            raise PermissionDenied('Non è possibile accedere a questa pagina perchè non sei il creatore della scelta')
        
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['poll'] = self.poll
        context['all_tokens'] = self.tokens.count()
        context['tokens_used'] = self.tokens.filter(used=True).count()
        context['tokens_available'] = self.tokens.filter(used=False).count()
        return context

    def get_queryset(self):
        tokens = self.tokens.order_by('used', '-id')
        links = [
            f"{self.request.scheme}://{self.request.get_host()}/{self.poll.mapping.code}/{token.get_password_for_url()}"
            for token in tokens
        ]
        return list(zip(tokens, links))

    def form_valid(self, form) -> http.HttpResponse:
        generated_tokens = generate_tokens(self.poll, form.cleaned_data['tokens_to_be_generated'])
        self.request.session['generated'] = generated_tokens
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse('polls:tokens_success', kwargs={'id': self.poll.id})
    
@login_required
def tokens_success(request: http.HttpRequest, id):
    return render(request, 'polls/tokens_generation_success.html', {
        'id': id,
        'generated': request.session.pop('generated', [])
    })

@login_required
def download_tokens(request: http.HttpRequest, id: int) -> http.FileResponse:
    poll = SearchPollService().search_by_id(id)
    if not isinstance(poll, TokenizedPoll):
        raise http.Http404('Questa scelta non prevede votazione tramite password')
    response = TicketGenerator(
        poll, 
        request.scheme if request.scheme is not None else "", 
        request.get_host()
        ).render()
    return response

class TokenDeleteView(LoginRequiredMixin, DeleteView):
    model = Token
    http_method_names = ['post']

    def get_object(self, queryset = None):
        token: Token = super().get_object(queryset) # type: ignore
        self.poll: Poll = token.poll # type: ignore

        if not isinstance(self.poll, TokenizedPoll):
            raise http.Http404('Questa scelta non prevede votazione tramite password')

        if self.poll.author != self.request.user:
            raise PermissionDenied('Non hai i permessi per eliminare questa password')

        if token.used:
            raise PermissionDenied('Non è possibile eliminare una password dopo che è stata utilizzata')
        
        if self.poll.is_ended():
            raise PermissionDenied('Non è possibile eliminare una password dopo che la votazione è terminata')
        
        return token
    
    def get_success_url(self) -> str:
        return reverse('polls:tokens', kwargs={'id': self.poll.id}) # type: ignore