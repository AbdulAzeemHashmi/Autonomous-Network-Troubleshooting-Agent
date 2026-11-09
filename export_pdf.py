"""
Export Phase 3 Markdown Report to Publication-Grade PDF using ReportLab
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Adds running headers and footers with dynamic page counts."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setFillColor(colors.HexColor("#64748B"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "Computer Networks — Phase 3: Autonomous Network Troubleshooting Agent")
            self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "FAST-NUCES")
            self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Footer
        self.line(54, 45, 8.5 * 72 - 54, 45)
        self.drawString(54, 32, "Abdul Azeem (24I-2013) & Taha Amjad (24K-0007)")
        self.drawRightString(8.5 * 72 - 54, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def convert_markdown_to_pdf(md_path: str, pdf_path: str):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        "CoverSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=14
    )
    meta_style = ParagraphStyle(
        "MetaStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    h3_style = ParagraphStyle(
        "Heading3_Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )
    caption_style = ParagraphStyle(
        "Caption_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#475569"),
        alignment=1,  # Center
        spaceBefore=4,
        spaceAfter=8
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )
    table_cell_header = ParagraphStyle(
        "TableCellHeader",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.white
    )

    story = []

    lines = md_text.split("\n")
    i = 0
    in_table = False
    table_lines = []

    while i < len(lines):
        line = lines[i].strip()

        # Handle Tables
        if line.startswith("|") and line.endswith("|"):
            table_lines.append(line)
            i += 1
            continue
        elif table_lines:
            # Process buffered table
            parsed_rows = []
            for t_line in table_lines:
                if re.match(r"^\|(\s*[-:]+\s*\|)+$", t_line):
                    continue  # Separator line
                cols = [c.strip() for c in t_line.split("|")[1:-1]]
                parsed_rows.append(cols)

            if parsed_rows:
                num_cols = len(parsed_rows[0])
                col_w = (doc.width) / float(num_cols)
                table_data = []
                for row_idx, r_cols in enumerate(parsed_rows):
                    row_cells = []
                    for c_idx, cell_text in enumerate(r_cols):
                        c_style = table_cell_header if row_idx == 0 else table_cell
                        clean_cell = cell_text.replace("**", "").replace("`", "")
                        row_cells.append(Paragraph(clean_cell, c_style))
                    table_data.append(row_cells)

                t = Table(table_data, colWidths=[col_w] * num_cols)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")])
                ]))
                story.append(t)
                story.append(Spacer(1, 6))

            table_lines = []

        if not line:
            i += 1
            continue

        # Handle Images
        img_match = re.search(r"!\[(.*?)\]\((.*?)\)", line)
        if img_match:
            img_caption = img_match.group(1)
            img_rel_path = img_match.group(2).replace("../", "")
            img_abs_path = os.path.abspath(img_rel_path)
            if os.path.exists(img_abs_path):
                img = Image(img_abs_path, width=420, height=220)
                img.hAlign = "CENTER"
                story.append(img)
                story.append(Paragraph(f"<b>Figure</b>: {img_caption}", caption_style))
            i += 1
            continue

        # Title / Subtitle
        if line.startswith("# "):
            title_text = line[2:].strip()
            story.append(Paragraph(title_text, title_style))
        elif line.startswith("## Project Title:"):
            story.append(Paragraph(line[3:].strip(), subtitle_style))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:].strip(), h1_style))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:].strip(), h2_style))
        elif line.startswith("#### "):
            story.append(Paragraph(line[5:].strip(), h3_style))
        elif line.startswith("---"):
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=8, spaceBefore=4))
        elif line.startswith("- ") or line.startswith("* "):
            clean_b = line[2:].strip().replace("**", "<b>").replace("`", "")
            # close bold tags properly
            if clean_b.count("<b>") % 2 != 0:
                clean_b += "</b>"
            clean_b = clean_b.replace("<b>", "<b>", 1)  # retain
            # replace pairs
            parts = clean_b.split("<b>")
            rebuilt = parts[0]
            for p in parts[1:]:
                if "</b>" not in p:
                    rebuilt += f"<b>{p}</b>"
                else:
                    rebuilt += f"<b>{p}"
            story.append(Paragraph(f"• {rebuilt}", bullet_style))
        elif re.match(r"^\d+\.\s+", line):
            story.append(Paragraph(line.replace("**", "<b>").replace("`", "") + ("</b>" if line.count("**") % 2 != 0 else ""), bullet_style))
        else:
            clean_p = line.replace("**", "<b>").replace("`", "")
            if clean_p.count("<b>") % 2 != 0:
                clean_p += "</b>"
            # Render italics
            clean_p = re.sub(r"\*(.*?)\*", r"<i>\1</i>", clean_p)
            story.append(Paragraph(clean_p, body_style))

        i += 1

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[+] Successfully exported PDF report to '{pdf_path}'")


if __name__ == "__main__":
    convert_markdown_to_pdf("docs/Phase3_Report.md", "docs/Phase3_Report.pdf")
