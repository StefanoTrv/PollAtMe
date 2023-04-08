import io
from typing import Any

from django import http
from django.db.models import QuerySet  # type: ignore
from reportlab.pdfgen import canvas  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.units import cm  # type: ignore

from reportlab_qrcode import QRCodeImage # type: ignore

from polls.models import Token, TokenizedPoll


def render_pdf(poll : TokenizedPoll, scheme, host) -> http.FileResponse:
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    width, height = A4
    p.grid([0, width / 2, width], [0, height / 4, height / 2, 3 * height / 4, height])

    token = poll.token_set.filter(used=False).first()
    link = f"{scheme}://{host}/{poll.mapping.code}/{token.token if token is not None else 'token'}"
    qr = QRCodeImage(link, size=3.5 * cm)

    qr.drawOn(p, 195, 5)
    start_y = 190
    start_x = 15
    p.drawString(start_x, start_y, "Vota la mia scelta")
    p.drawString(start_x, start_y-20, f"1) Vai sul sito:")
    p.drawString(start_x, start_y-40, f"{scheme}://sceglimeglio.azurewebsites.net/{poll.mapping.code}")
    p.drawString(start_x, start_y-60, f"2) Inserisci il codice:")
    p.drawString(start_x, start_y-80, f"{token.token if token is not None else 'token'}")
    p.drawString(start_x, start_y-100, "OPPURE")
    p.drawString(start_x, start_y-120, "Scansiona il QR code")
    p.drawString(start_x, start_y-150, f"Valido dal {poll.start.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(start_x, start_y-170, f"al {poll.end.strftime('%d/%m/%Y %H:%M')}")

    qr.drawOn(p, 195 + (width / 2), 5 + (height / 4))
    start_y = 190 + (height / 4)
    start_x = 15 + (width / 2)
    p.drawString(start_x, start_y, "Vota la mia scelta")
    p.drawString(start_x, start_y-20, f"1) Vai sul sito:")
    p.drawString(start_x, start_y-40, f"{scheme}://sceglimeglio.azurewebsites.net/{poll.mapping.code}")
    p.drawString(start_x, start_y-60, f"2) Inserisci il codice:")
    p.drawString(start_x, start_y-80, f"{token.token if token is not None else 'token'}")
    p.drawString(start_x, start_y-100, "OPPURE")
    p.drawString(start_x, start_y-120, "Scansiona il QR code")
    p.drawString(start_x, start_y-150, f"Valido dal {poll.start.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(start_x, start_y-170, f"al {poll.end.strftime('%d/%m/%Y %H:%M')}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return http.FileResponse(buffer, as_attachment=False, filename='tickets.pdf')