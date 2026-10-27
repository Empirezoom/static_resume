import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
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
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Anthony Oluwaseun Matthew — Statement of Purpose (M.Sc. Artificial Intelligence)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 34, text)
        self.drawString(54, 34, "Confidential — Academic Application Portfolio | empirecodes.com.ng")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        self.restoreState()


def build_unibo_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=54
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569")
    )
    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    meta_val = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )
    section_h1 = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=11,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13.8,
        textColor=colors.HexColor("#1E293B"),
        alignment=4,
        spaceAfter=7
    )
    sig_style = ParagraphStyle(
        'Sig',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#334155")
    )

    story = []
    story.append(Paragraph("STATEMENT OF PURPOSE", title_style))
    story.append(Paragraph(
        "<b>Applicant:</b> Anthony Oluwaseun Matthew &nbsp;|&nbsp; <b>Academic Background:</b> B.Tech in Mathematics (Operations Research & Computational Mathematics), OAUSTECH",
        subtitle_style
    ))
    story.append(Spacer(1, 6))

    meta_data = [
        [Paragraph("<b>Target Program:</b>", meta_label), Paragraph("Master of Science (Laurea Magistrale) in Artificial Intelligence", meta_val)],
        [Paragraph("<b>Target Institution:</b>", meta_label), Paragraph("Alma Mater Studiorum - Università di Bologna (Department of Computer Science and Engineering)", meta_val)],
        [Paragraph("<b>Official Contacts:</b>", meta_label), Paragraph("ceo@empirecodes.com.ng &nbsp;|&nbsp; matthew@empirecodes.com.ng &nbsp;|&nbsp; +234 817 305 7810", meta_val)],
        [Paragraph("<b>Engineering Portfolio:</b>", meta_label), Paragraph('<a href="https://empirecodes.com.ng" color="#0284C7">empirecodes.com.ng</a> &nbsp;|&nbsp; GitHub: <a href="https://github.com/Empirezoom" color="#0284C7">github.com/Empirezoom</a>', meta_val)]
    ]
    t = Table(meta_data, colWidths=[1.4 * inch, 5.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

    sections = [
        {
            "heading": "1. INTRODUCTION & ACADEMIC FOUNDATION",
            "paragraphs": [
                "My journey into advanced artificial intelligence is anchored in a foundational conviction: the most resilient, intelligent computing systems are derived from deterministic mathematical principles. Having completed my Bachelor of Technology in Mathematics at Olusegun Agagu University of Science and Technology (OAUSTECH), specializing in Operations Research and Computational Mathematics, I approach software engineering and machine learning not as empirical heuristics, but as the rigorous formulation of constrained optimization models, stochastic processes, and high-dimensional linear algebraic transformations.",
                "Over the past five years, I have actively bridged this theoretical background with large-scale production engineering—architecting cross-platform mobile ecosystems, deploying zero-loss transaction pipelines with idempotent concurrency controls, and managing decoupled cloud microservices. I am now applying to the Master of Science (Laurea Magistrale) in Artificial Intelligence at Alma Mater Studiorum - Università di Bologna to advance my theoretical mastery of deep learning foundations, distributed autonomous systems, and formal verification methodologies."
            ]
        },
        {
            "heading": "2. BRIDGING COMPUTATIONAL MATHEMATICS & REAL-WORLD SYSTEMS",
            "paragraphs": [
                "Throughout my undergraduate studies, advanced coursework in Numerical Analysis, Optimization Theory, and Discrete Mathematics revealed how mathematical constraints dictate real-world algorithmic efficiency. In my engineering practice, I utilized these exact analytical frameworks to eliminate critical bottlenecks across mission-critical systems.",
                "For instance, when architecting the transactional pipeline for a high-volume platform processing live payments via the Paystack gateway, concurrency and cellular network latency created substantial risks for duplicate ledger credits and state drift. Applying database transaction isolation theory, I implemented atomic row-level locks (SELECT FOR UPDATE) and cryptographic HMAC-SHA512 webhook signature verification. To ensure zero data discrepancy, I designed an idempotent event-driven queueing architecture with exponential backoff workers. This rigorous mathematical approach eliminated 100% of transaction race conditions and guaranteed ledger consistency across volatile network conditions."
            ]
        },
        {
            "heading": "3. PROFESSIONAL EXPERIENCE & SYSTEMS ARCHITECTURE",
            "paragraphs": [
                "My professional progression has reinforced my capacity to engineer and maintain decoupled systems across the full software stack. Under my software firm, EmpireCodes, I designed, developed, and published a complete cross-platform mobile and web fleet. Utilizing React Native and Expo SDK, I engineered production mobile applications incorporating offline-first state reconciliation with asynchronous storage and synchronized audio-haptic micro-interactions. On the backend, I designed high-throughput RESTful APIs using Python and Django REST Framework, containerized with Docker and deployed across cloud microservices.",
                "In addition to commercial systems architecture, I served as a Backend Developer and Technical Instructor at AnchorSoft Academy in Lagos, mentoring aspiring engineers in relational database normalization, API security, and Python development. Furthermore, during my National Youth Service Corps (NYSC) deployment within the Procurement Unit of the Somolu Local Government Council (completed 2026), I identified severe manual record-keeping bottlenecks and engineered an automated municipal budget tracking pipeline using Python and relational database schemas, reducing procurement processing turnaround by 40%."
            ]
        },
        {
            "heading": "4. WHY UNIVERSITÀ DI BOLOGNA & CAREER OBJECTIVES",
            "paragraphs": [
                "Alma Mater Studiorum - Università di Bologna holds a legendary reputation as the oldest university in the Western world and a contemporary powerhouse in European computer science and artificial intelligence research. The Master of Science in Artificial Intelligence at the Bologna Campus offers the exact intellectual rigor and breadth that matches my analytical foundation.",
                "I am particularly drawn to the Department of Computer Science and Engineering (DISI) and its specialized curriculum covering Deep Learning, Knowledge Representation and Reasoning, and Autonomous Distributed Systems. The program's balance of foundational mathematical depth and advanced AI application aligns directly with my goal of becoming an AI Systems Architect capable of designing secure, scalable intelligent architectures. Having completed my undergraduate degree in English with certified proficiency, I am fully prepared to integrate into Bologna's international academic environment.",
                "Following graduation, my career objective is to operate as a Lead Systems Architect and Distributed AI Researcher, contributing to mission-critical infrastructure, autonomous software verification, and high-security fintech pipelines."
            ]
        },
        {
            "heading": "5. CONCLUSION",
            "paragraphs": [
                "I bring to the University of Bologna a unique blend of theoretical mathematical training, five years of verified production software engineering, and an unyielding commitment to academic excellence. I am fully prepared to meet the academic and research demands of your graduate faculty, and I look forward to contributing actively to your international scholar community.",
                "Thank you for considering my application."
            ]
        }
    ]

    for sec in sections:
        story.append(Paragraph(sec["heading"], section_h1))
        story.append(HRFlowable(width="100%", thickness=0.75, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=5))
        for p in sec["paragraphs"]:
            story.append(Paragraph(p, body_style))

    story.append(Spacer(1, 6))
    sign_off = [
        "<b>Respectfully submitted,</b>",
        "<br/>",
        "<b>Anthony Oluwaseun Matthew</b>",
        "Founder & Lead Engineer, EmpireCodes",
        "B.Tech in Mathematics (Honours), OAUSTECH",
        "Email: ceo@empirecodes.com.ng | matthew@empirecodes.com.ng",
        "Phone: +234 817 305 7810 / +234 813 536 2561",
        'Portfolio: <a href="https://empirecodes.com.ng" color="#0284C7">https://empirecodes.com.ng</a>'
    ]
    story.append(Paragraph("<br/>".join(sign_off), sig_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {output_path}")


if __name__ == '__main__':
    paths = [
        r'C:\Users\PC\Downloads\empirecodes_edit_now\empirecodes\Statement_of_Purpose_University_of_Bologna.pdf',
        r'C:\Users\PC\Downloads\empirecodes_edit_now\Statement_of_Purpose_University_of_Bologna.pdf',
        r'C:\Users\PC\Downloads\Statement_of_Purpose_University_of_Bologna.pdf',
        r'C:\Users\PC\Downloads\empirecodes_edit_now\empirecodes\Statement_of_Purpose_UniBo.pdf',
        r'C:\Users\PC\Downloads\empirecodes_edit_now\Statement_of_Purpose_UniBo.pdf',
        r'C:\Users\PC\Downloads\Statement_of_Purpose_UniBo.pdf',
        r'C:\Users\PC\Downloads\empirecodes_edit_now\empirecodes\UNIBO_APPLICATION_UPLOADS\5_Statement_of_Purpose_UniBo.pdf'
    ]

    primary = paths[0]
    build_unibo_pdf(primary)

    for p in paths[1:]:
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            shutil.copyfile(primary, p)
            print(f"Copied to: {p}")
        except Exception as e:
            print(f"Failed copying to {p}: {e}")
