#!/usr/bin/env python3
"""Generate the sample PDFs used to test converting-pdf-for-agents.

  python examples/make_sample_pdf.py [out.pdf]               sample-handbook.pdf: text, 2 ruled tables, images
  python examples/make_sample_pdf.py out.pdf --no-images     same text and tables, no images at all

The image version holds: a PNG chart with a "Figure 1" caption (page 2), the same PNG again without caption (page 4,
tests de-duplication), a JPEG photo without caption (page 3), a drawn (vector) bar chart with a "Figure 2" caption
(page 3, extracted only with --vector-figures), a 32 px icon (page 1, skipped as too small) and a logo on every
page (skipped as repeated decoration).
Requires reportlab and Pillow (test-only; the converter itself needs only pdfplumber).
"""
import io
import sys

from PIL import Image, ImageDraw
from reportlab.graphics.shapes import Drawing, Line, Rect, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.platypus import Image as RLImage

args = [a for a in sys.argv[1:] if not a.startswith("--")]
with_images = "--no-images" not in sys.argv
out = args[0] if args else "sample-handbook.pdf"
ss = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=20, spaceAfter=10)
h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=15, spaceAfter=6)
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=10.5, leading=15)
cap = ParagraphStyle("c", parent=body, fontSize=9, textColor=colors.HexColor("#444444"))


def table(rows):
    t = Table(rows, hAlign="LEFT", colWidths=[4.5 * cm, 4 * cm, 6 * cm])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.7, colors.black), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                           ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]))
    return t


def png_chart():
    im = Image.new("RGB", (600, 300), "white")
    d = ImageDraw.Draw(im)
    for i, (h, c) in enumerate([(120, "#2b6cb0"), (170, "#2f855a"), (220, "#c05621")]):
        d.rectangle([80 + i * 150, 260 - h, 160 + i * 150, 260], fill=c)
    d.line([60, 260, 560, 260], fill="black", width=2)
    d.text((220, 10), "Leave days by service band", fill="black")
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def jpeg_photo():
    im = Image.new("RGB", (400, 260))
    px = im.load()
    for x in range(400):
        for y in range(260):
            px[x, y] = (x * 255 // 400, y * 255 // 260, 160)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return buf.getvalue()


def small(size, colour):
    buf = io.BytesIO()
    Image.new("RGB", (size, size), colour).save(buf, "PNG")
    return buf.getvalue()


def vector_chart():
    d = Drawing(380, 160)
    d.add(Line(30, 20, 370, 20))
    d.add(Line(30, 20, 30, 150))
    for i, (h, c) in enumerate([(50, colors.HexColor("#2b6cb0")), (110, colors.HexColor("#2f855a")),
                                (80, colors.HexColor("#c05621")), (30, colors.HexColor("#805ad5"))]):
        d.add(Rect(60 + i * 80, 20, 50, h, fillColor=c, strokeColor=colors.black))
    d.add(Line(30, 100, 370, 100, strokeDashArray=[3, 3]))
    return d


png, jpg = png_chart(), jpeg_photo()
logo = ImageReader(io.BytesIO(small(100, "#555555")))


def footer(c, d):
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 1.2 * cm, "Acme Employee Handbook - Confidential")
    c.drawRightString(19 * cm, 1.2 * cm, f"Page {d.page}")
    if with_images:
        c.drawImage(logo, 17.5 * cm, 27.5 * cm, width=1.5 * cm, height=1.5 * cm)


def pic(data, w):
    return RLImage(io.BytesIO(data), width=w, height=w * (300 / 600 if data is png else 260 / 400))


s = []
s += [Paragraph("Acme Employee Handbook", h1),
      Paragraph("This handbook explains how Acme handles leave, expenses and remote work. "
                "It applies to all full-time employees and is reviewed every year.", body)]
if with_images:
    s += [Spacer(1, 6), RLImage(io.BytesIO(small(32, "#c53030")), width=0.9 * cm, height=0.9 * cm, hAlign="LEFT")]
s += [PageBreak(),
      Paragraph("Leave policy", h1),
      Paragraph("Employees accrue paid leave every month. Leave must be requested in advance through the HR portal. "
                "Managers approve or decline requests within three working days.", body), Spacer(1, 8),
      Paragraph("Annual leave", h2),
      Paragraph("Full-time employees receive the entitlement shown below, which grows with years of service.", body), Spacer(1, 6),
      table([["Years of service", "Days per year", "Notes"], ["0-2", "20", "Pro-rated in first year"],
             ["3-5", "23", "Carry over up to 5 days"], ["6+", "26", "Carry over up to 10 days"]]), Spacer(1, 8)]
if with_images:
    s += [pic(png, 9 * cm), Paragraph("Figure 1: Leave entitlement by years of service", cap), Spacer(1, 6)]
s += [Paragraph("Sick leave", h2),
      Paragraph("Notify your manager before your shift starts. A medical certificate is required after three days.", body),
      PageBreak(),
      Paragraph("Expense claims", h1),
      Paragraph("Submit claims within 30 days of purchase. Attach itemised receipts. Steps:", body),
      Paragraph("1. Create the claim in the finance portal.", body), Paragraph("2. Attach receipts.", body),
      Paragraph("3. Submit for manager approval.", body), Spacer(1, 6)]
if with_images:
    s += [pic(jpg, 6 * cm), Spacer(1, 10), vector_chart(), Paragraph("Figure 2: Spending by category", cap), Spacer(1, 6)]
s += [Paragraph("Spending limits", h2),
      table([["Category", "Limit (USD)", "Approval"], ["Meals", "50 per day", "Manager"],
             ["Travel", "1,500 per trip", "Director"], ["Equipment", "500", "IT and manager"]]), PageBreak(),
      Paragraph("Remote work", h1),
      Paragraph("Employees may work remotely up to three days a week. Use the company VPN and keep your equipment secure. "
                "Agree your working pattern with your manager and record it in the HR portal.", body)]
if with_images:
    s += [Spacer(1, 8), pic(png, 7 * cm)]
SimpleDocTemplate(out, pagesize=A4, title="Acme Employee Handbook").build(s, onFirstPage=footer, onLaterPages=footer)
print("wrote", out)
