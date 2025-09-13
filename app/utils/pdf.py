"""
PDF generation utilities using ReportLab.
"""
from collections.abc import Mapping, Sequence
from io import BytesIO
from typing import Any

import httpx
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_simple_pdf(title: str, lines: list[str], subtitle: str | None = None) -> bytes:
    """
    Create a simple PDF with a title and a list of text lines.
    Returns PDF bytes suitable for application/pdf responses.
    """
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 30 * mm
    c.setFont("Helvetica-Bold", 16)
    c.drawString(20 * mm, y, title)
    y -= 10 * mm
    if subtitle:
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.grey)
        c.drawString(20 * mm, y, subtitle)
        c.setFillColor(colors.black)
        y -= 8 * mm

    c.setFont("Helvetica", 10)
    for line in lines:
        if y < 20 * mm:
            c.showPage()
            y = height - 20 * mm
            c.setFont("Helvetica", 10)
        c.drawString(20 * mm, y, line)
        y -= 6 * mm

    c.showPage()
    c.save()
    pdf = buf.getvalue()
    buf.close()
    return pdf


def _fetch_image_bytes(url: str, timeout: float = 5.0) -> bytes | None:
    """Best-effort fetch of an image URL; returns bytes or None on failure."""
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            r = client.get(url)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
                return r.content
    except Exception:
        return None
    return None


def generate_table_pdf(
    title: str,
    subtitle: str | None,
    headers: Sequence[str],
    rows: Sequence[Sequence[Any]],
    totals: Mapping[str, Any] | None = None,
    logo_url: str | None = None,
) -> bytes:
    """
    Generate a branded PDF with an optional logo, title/subtitle, and a styled table.

    - headers: list of column labels
    - rows: list of row lists (values will be str()'d)
    - totals: optional mapping of header -> value; when provided, a totals row is appended
    - logo_url: optional URL to a logo image (fetched best-effort)
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()

    story: list[Any] = []

    # Header with optional logo
    img_width = 0
    if logo_url:
        img_bytes = _fetch_image_bytes(logo_url)
        if img_bytes:
            try:
                image = Image(BytesIO(img_bytes))
                # Fit logo width to ~30mm maintaining aspect ratio
                target_w = 30 * mm
                w, h = image.wrap(0, 0)
                if w and h:
                    scale = target_w / w
                    image.drawWidth = target_w
                    image.drawHeight = h * scale
                story.append(image)
                img_width = target_w
            except Exception:
                pass

    # Title and subtitle
    if title:
        title_para = Paragraph(f"<b>{title}</b>", styles["Title"])  # Large bold title
        story.append(title_para)
    if subtitle:
        subtitle_para = Paragraph(f"<font color='#666666'>{subtitle}</font>", styles["Normal"])  # Grey subtitle
        story.append(Spacer(1, 6))
        story.append(subtitle_para)

    story.append(Spacer(1, 12))

    # Build table data
    data: list[list[str]] = [list(map(str, headers))]
    for r in rows:
        data.append(["" if v is None else (f"{v:.2f}" if isinstance(v, (int, float)) else str(v)) for v in r])

    if totals:
        # Create a totals row aligned with headers
        totals_row = []
        for h in headers:
            v = totals.get(h)
            if isinstance(v, (int, float)):
                totals_row.append(f"{v:.2f}")
            else:
                totals_row.append(str(v) if v is not None else "")
        data.append(totals_row)

    tbl = Table(data, hAlign='LEFT')
    tbl_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.95)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.Color(0.8, 0.8, 0.8)),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    # If totals present, style the last row
    if totals:
        last_idx = len(data) - 1
        tbl_style.add('BACKGROUND', (0, last_idx), (-1, last_idx), colors.Color(0.95, 0.95, 0.90))
        tbl_style.add('FONTNAME', (0, last_idx), (-1, last_idx), 'Helvetica-Bold')

    tbl.setStyle(tbl_style)
    story.append(tbl)

    doc.build(story)
    pdf = buf.getvalue()
    buf.close()
    return pdf
