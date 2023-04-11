import io
from typing import Any

from django import http
from django.core.paginator import Paginator
from django.db.models import QuerySet
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import cm  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
from reportlab_qrcode import QRCodeImage  # type: ignore

from polls.models import Token, TokenizedPoll


class TicketGenerator:
    buffer = io.BytesIO()
    width, height = A4

    TICKETS_PER_ROW = 2
    TICKETS_PER_COLUMN = 4
    TICKETS_PER_PAGE = TICKETS_PER_ROW * TICKETS_PER_COLUMN

    def __init__(self, poll: TokenizedPoll, scheme: str, host: str) -> None:
        self.poll = poll
        self.base_url = f"{scheme}://{host}/{poll.mapping.code}/"
        self.p = canvas.Canvas(self.buffer)
        self.tokens = self.poll.token_set.filter(used=False)

        self.TICKET_WIDTH = self.width / self.TICKETS_PER_ROW
        self.TICKET_HEIGHT = self.height / self.TICKETS_PER_COLUMN
    
    def print_ticket(self, token: Token, offset_x, offset_y) -> None:
        link = f"{self.base_url}{token.token.replace(' ', '-')}"
        qr = QRCodeImage(link, size=3.5 * cm, border=1)
        qr.drawOn(self.p, offset_x + 195, offset_y + 5)

        start_x = offset_x + 15
        start_y = offset_y + 190
        self.p.saveState()
        self.p.setFont("Helvetica-Bold", 16)
        self.p.drawString(start_x, start_y, "Vota la mia scelta")

        self.p.restoreState()
        self.p.drawString(start_x, start_y-20, "1) Vai sul sito:")
        self.p.drawString(start_x, start_y-40, self.base_url)
        self.p.drawString(start_x, start_y-60, "2) Inserisci il codice:")

        self.p.saveState()
        self.p.setFont("Helvetica-Bold", 13)
        self.p.drawString(start_x, start_y-80, token.token)
        
        self.p.restoreState()
        self.p.drawString(start_x, start_y-100, "OPPURE")
        self.p.drawString(start_x, start_y-120, "Scansiona il QR code")
        self.p.drawString(start_x, start_y-150, "Potrai votare fino al")
        self.p.drawString(start_x, start_y-170, self.poll.end.strftime('%d/%m/%Y %H:%M'))
    
    def print_grid_on_page(self) -> None:
        self.p.grid(
            [ i * self.TICKET_WIDTH for i in range(self.TICKETS_PER_ROW + 1) ], 
            [ i * self.TICKET_HEIGHT for i in range(self.TICKETS_PER_COLUMN + 1) ]
        )

    def render(self) -> http.FileResponse:
        paginator = Paginator(self.tokens, self.TICKETS_PER_PAGE)

        for page in paginator.page_range:
            self.print_grid_on_page()
            # L'origine è in basso a sinistra, i ticket vanno stampati dall'alto verso il basso
            offset_y = (self.TICKETS_PER_COLUMN - 1) * self.TICKET_HEIGHT
            rows = Paginator(paginator.page(page).object_list, 2)
            for row in rows.page_range:
                offset_x = 0
                for ticket in rows.page(row).object_list:
                    self.print_ticket(ticket, offset_x, offset_y)
                    offset_x += self.TICKET_WIDTH
                offset_y -= self.TICKET_HEIGHT
            self.p.showPage()
        self.p.save()
        self.buffer.seek(0)
        return http.FileResponse(self.buffer, as_attachment=False, filename='tickets.pdf')