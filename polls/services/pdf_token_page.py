import io

from django import http
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import cm  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
from reportlab_qrcode import QRCodeImage  # type: ignore

from polls.models import Token, TokenizedPoll

""" The TicketGenerator class takes a TokenizedPoll instance, scheme (e.g., http or https), and host as input.
    It uses the reportlab library to generate a PDF document containing multiple tickets.
    It generates printable tickets for a TokenizedPoll, including QR codes and instructions for voting."""
class TicketGenerator:
    width, height = A4

    TICKETS_PER_ROW = 2
    TICKETS_PER_COLUMN = 4
    TICKETS_PER_PAGE = TICKETS_PER_ROW * TICKETS_PER_COLUMN

    def __init__(self, poll: TokenizedPoll, scheme: str, host: str) -> None:
        self.buffer = io.BytesIO()
        self.poll = poll
        self.base_url = f"{scheme}://{host}/{poll.mapping.code}"
        self.p = canvas.Canvas(self.buffer)
        self.tokens = self.poll.token_set.filter(used=False).order_by('-id')

        self.TICKET_WIDTH = self.width / self.TICKETS_PER_ROW
        self.TICKET_HEIGHT = self.height / self.TICKETS_PER_COLUMN
    
    """ Prints a single ticket on the PDF canvas.
        It includes a QR code, instructions, and other details specific to each ticket."""
    def print_ticket(self, token: Token, offset_x, offset_y) -> None:
        link = f"{self.base_url}/{token.get_password_for_url()}"
        qr = QRCodeImage(link, size=3.5 * cm, border=1)
        qr.drawOn(self.p, offset_x + 195, offset_y + 5)

        start_x = offset_x + 15
        start_y = offset_y + 190
        spacing = 20

        self.p.saveState()
        self.p.setFont("Helvetica-Bold", 16)
        self.p.drawString(start_x, start_y, "Vota la mia scelta")

        self.p.restoreState()
        self.p.drawString(start_x, start_y-spacing, "1) Vai sul sito:")
        self.p.drawString(start_x, start_y-(2*spacing), self.base_url)
        self.p.drawString(start_x, start_y-(3*spacing), "2) Inserisci la password:")

        self.p.saveState()
        self.p.setFont("Helvetica-Bold", 13)
        self.p.drawString(start_x, start_y-(4*spacing), token.token)
        
        self.p.restoreState()
        self.p.drawString(start_x, start_y-(5*spacing), "OPPURE")
        self.p.drawString(start_x, start_y-(6*spacing), "Scansiona il QR code")
        self.p.drawString(start_x, start_y-(7*spacing + 10), "Potrai votare fino al")
        self.p.drawString(start_x, start_y-(8*spacing + 10), self.poll.end.astimezone().strftime('%d/%m/%Y %H:%M'))
    
    """Draws grid lines on the PDF page to separate individual tickets."""
    def print_grid_on_page(self) -> None:
        self.p.grid(
            [ i * self.TICKET_WIDTH for i in range(self.TICKETS_PER_ROW + 1) ], 
            [ i * self.TICKET_HEIGHT for i in range(self.TICKETS_PER_COLUMN + 1) ]
        )


    """ Generates the PDF by iterating over the tokens, organizing them into pages and rows, and calling the print_ticket method for each token.
        The generated PDF is returned as an HTTP response."""
    def render(self) -> http.FileResponse:
        paginator = Paginator(self.tokens, self.TICKETS_PER_PAGE)

        for page in paginator.page_range:
            self.print_grid_on_page()
            # The origin is bottom left. The tickets must be printed starting from the top to bottom
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
        return http.FileResponse(self.buffer, as_attachment=False, filename=f"tickets-{self.poll.pk}.pdf")