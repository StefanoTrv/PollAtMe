from typing import Any
from django.db.models import QuerySet # type: ignore
from django import http
from xhtml2pdf import pisa # type: ignore
from django.template.loader import get_template

from polls.models import TokenizedPoll, Token

def response_to_pdf(html):
    response = http.HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    
    pisa_status = pisa.CreatePDF(
        html, dest=response
    )

    if pisa_status.err:
       return http.HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

def generate_pdf(poll : TokenizedPoll, scheme, host) -> http.HttpResponse:
    template = get_template('polls/tickets.html')
    context: dict[str, Any] = {
        'links': [
            f"{scheme}://{host}/{poll.mapping.code}/{token.token}/"
            for token in poll.token_set.filter(used=False)
        ],
        'poll': poll,
    }
    html = template.render(context)

    return response_to_pdf(html)
    #return http.HttpResponse(html)