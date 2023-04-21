
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
from polls.services import check
from django.urls import reverse


class TokensView(LoginRequiredMixin, FormView, ListView):
    template_name = 'polls/tokens_page.html'
    form_class = TokenGeneratorForm
    paginate_by = 12

    def dispatch(self, request, *args, **kwargs):
        self.poll = SearchPollService().search_by_id(kwargs['id'])
        self.tokens = Token.objects.filter(poll = self.poll)

        passed = check.CheckPollOwnership(self.poll, request.user).handle()
        
        return passed if passed else super().dispatch(request, *args, **kwargs)

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

    check.CheckPollAuthenticationType(poll, TokenizedPoll).handle()
    
    response = TicketGenerator(
        poll, # type: ignore
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

        handler = check.CheckPollAuthenticationType(self.poll, TokenizedPoll)
        handler.set_next(check.CheckPollOwnership(self.poll, self.request.user))
        handler.set_next(check.CheckTokenNotUsed(token))
        handler.set_next(check.CheckPollIsNotEnded(self.poll))
        handler.handle()
        
        return token
    
    def get_success_url(self) -> str:
        return reverse('polls:tokens', kwargs={'id': self.poll.id}) # type: ignore