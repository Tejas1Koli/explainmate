from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import os

def export_notes_to_pdf(notes, filename="ExplainMate_Notes.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    # Add a Unicode font (DejaVuSans)
    font_dir = os.path.join(os.path.dirname(__file__), "dejavu-fonts-ttf-2.37", "ttf")
    font_regular = os.path.join(font_dir, "DejaVuSans.ttf")
    font_bold = os.path.join(font_dir, "DejaVuSans-Bold.ttf")
    if not os.path.exists(font_regular) or not os.path.exists(font_bold):
        raise FileNotFoundError(
            f"DejaVuSans.ttf or DejaVuSans-Bold.ttf not found in {font_dir}. "
            "Please ensure both files exist."
        )
    pdf.add_font('DejaVu', '', font_regular, uni=True)
    pdf.add_font('DejaVu', 'B', font_bold, uni=True)
    pdf.set_font('DejaVu', '', 16)
    pdf.cell(0, 10, "ExplainMate Notes", ln=True, align='C')
    pdf.ln(10)
    for note in notes:
        question = note.get('question', '')
        content = note.get('content', '')
        # If content is a list (bullet points), join as lines for PDF
        if isinstance(content, list):
            content = '\n'.join(content)
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, f"Q: {question}", ln=True)
        pdf.set_font('DejaVu', '', 10)
        date_str = note.get('timestamp', '')
        if date_str:
            try:
                date_str = datetime.fromisoformat(date_str).strftime('%Y-%m-%d %H:%M')
            except ValueError:
                date_str = "Invalid date format"
        pdf.cell(0, 8, f"Date: {date_str}", ln=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 8, content)
        pdf.ln(5)
    pdf_output = BytesIO()
    pdf.output(pdf_output, 'F')
    pdf_output.seek(0)
    return pdf_output
