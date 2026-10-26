import os
import zipfile
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute total page count and add running footer."""
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
        # Running top header on pages 2+
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Anthony Oluwaseun Matthew — Statement of Purpose (M.Sc. Computer Science)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running bottom footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 34, text)
        self.drawString(54, 34, "Confidential — Academic Application Portfolio | empirecodes.com.ng")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)
        self.restoreState()


def build_pdf(filename, target_title, target_program, target_institutions, body_paragraphs):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=50,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
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
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.2,
        textColor=colors.HexColor("#1E293B"),
        alignment=4,  # Justified
        spaceAfter=8
    )
    sig_style = ParagraphStyle(
        'Sig',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )

    story = []

    # Title & Applicant Header
    story.append(Paragraph(target_title, title_style))
    story.append(Paragraph(
        "<b>Applicant:</b> Anthony Oluwaseun Matthew &nbsp;|&nbsp; <b>Academic Background:</b> B.Tech in Mathematics (Operations Research & Computational Mathematics), OAUSTECH",
        subtitle_style
    ))
    story.append(Spacer(1, 6))

    # Meta box
    meta_data = [
        [Paragraph("<b>Target Program:</b>", meta_label), Paragraph(target_program, meta_val)],
        [Paragraph("<b>Target Institutions:</b>", meta_label), Paragraph(target_institutions, meta_val)],
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
    story.append(Spacer(1, 10))

    # Body sections
    for sec in body_paragraphs:
        if sec.get('heading'):
            story.append(Paragraph(sec['heading'], section_h1))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceBefore=1, spaceAfter=6))
        for p in sec['paragraphs']:
            story.append(Paragraph(p, body_style))

    # Sign-off
    story.append(Spacer(1, 8))
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
    print(f"Generated PDF successfully: {filename}")


def create_docx(filename, title, applicant, target_program, target_institutions, body_sections):
    """Generate a clean, fully-compatible Microsoft Word .docx file using built-in zipfile & standard OpenXML."""
    doc_xml_parts = []
    doc_xml_parts.append('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    doc_xml_parts.append('<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">')
    doc_xml_parts.append('<w:body>')

    # Title
    doc_xml_parts.append(
        f'<w:p><w:pPr><w:jc w:val="left"/><w:spacing w:after="80"/></w:pPr>'
        f'<w:r><w:rPr><w:b/><w:sz w:val="34"/><w:color w:val="0F172A"/></w:rPr>'
        f'<w:t>{escape(title)}</w:t></w:r></w:p>'
    )

    # Subtitle
    sub = f"Applicant: {applicant} | B.Tech in Mathematics (Operations Research & Computational Mathematics), OAUSTECH"
    doc_xml_parts.append(
        f'<w:p><w:pPr><w:spacing w:after="160"/></w:pPr>'
        f'<w:r><w:rPr><w:i/><w:sz w:val="20"/><w:color w:val="475569"/></w:rPr>'
        f'<w:t>{escape(sub)}</w:t></w:r></w:p>'
    )

    # Metadata block
    meta_lines = [
        ("Target Program", target_program),
        ("Target Institutions", target_institutions),
        ("Contacts", "ceo@empirecodes.com.ng | matthew@empirecodes.com.ng | +234 817 305 7810"),
        ("Engineering Portfolio", "https://empirecodes.com.ng | GitHub: https://github.com/Empirezoom")
    ]
    for lbl, val in meta_lines:
        doc_xml_parts.append(
            f'<w:p><w:pPr><w:spacing w:after="40"/></w:pPr>'
            f'<w:r><w:rPr><w:b/><w:sz w:val="19"/><w:color w:val="1E293B"/></w:rPr><w:t>{escape(lbl)}: </w:t></w:r>'
            f'<w:r><w:rPr><w:sz w:val="19"/><w:color w:val="334155"/></w:rPr><w:t>{escape(val)}</w:t></w:r>'
            f'</w:p>'
        )

    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="200"/></w:pPr></w:p>')

    # Body sections
    for sec in body_sections:
        if sec.get('heading'):
            doc_xml_parts.append(
                f'<w:p><w:pPr><w:spacing w:before="240" w:after="80"/><w:pBdr><w:bottom w:val="single" w:sz="6" w:space="4" w:color="CBD5E1"/></w:pBdr></w:pPr>'
                f'<w:r><w:rPr><w:b/><w:sz w:val="23"/><w:color w:val="0F172A"/></w:rPr>'
                f'<w:t>{escape(sec["heading"])}</w:t></w:r></w:p>'
            )
        for p in sec['paragraphs']:
            clean_p = p.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
            doc_xml_parts.append(
                f'<w:p><w:pPr><w:jc w:val="both"/><w:spacing w:after="140" w:line="276" w:lineRule="auto"/></w:pPr>'
                f'<w:r><w:rPr><w:sz w:val="21"/><w:color w:val="1E293B"/></w:rPr>'
                f'<w:t xml:space="preserve">{escape(clean_p)}</w:t></w:r></w:p>'
            )

    # Signoff
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:before="240" w:after="60"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="20"/></w:rPr><w:t>Respectfully submitted,</w:t></w:r></w:p>')
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="20"/></w:rPr><w:t>Anthony Oluwaseun Matthew</w:t></w:r></w:p>')
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr><w:sz w:val="19"/><w:color w:val="475569"/></w:rPr><w:t>Founder &amp; Lead Engineer, EmpireCodes</w:t></w:r></w:p>')
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr><w:sz w:val="19"/><w:color w:val="475569"/></w:rPr><w:t>B.Tech in Mathematics (Honours), OAUSTECH</w:t></w:r></w:p>')
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr><w:sz w:val="19"/><w:color w:val="475569"/></w:rPr><w:t>Email: ceo@empirecodes.com.ng | matthew@empirecodes.com.ng</w:t></w:r></w:p>')
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr><w:sz w:val="19"/><w:color w:val="475569"/></w:rPr><w:t>Phone: +234 817 305 7810 / +234 813 536 2561</w:t></w:r></w:p>')
    doc_xml_parts.append('<w:p><w:pPr><w:spacing w:after="40"/></w:pPr><w:r><w:rPr><w:sz w:val="19"/><w:color w:val="475569"/></w:rPr><w:t>Portfolio: https://empirecodes.com.ng</w:t></w:r></w:p>')

    doc_xml_parts.append('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>')
    doc_xml_parts.append('</w:body></w:document>')
    doc_xml = "".join(doc_xml_parts)

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '</Types>'
    )
    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '</Relationships>'
    )
    doc_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
    )

    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as docx:
        docx.writestr('[Content_Types].xml', content_types_xml)
        docx.writestr('_rels/.rels', rels_xml)
        docx.writestr('word/_rels/document.xml.rels', doc_rels_xml)
        docx.writestr('word/document.xml', doc_xml)

    print(f"Generated DOCX successfully: {filename}")


# Shared Body Paragraphs Content
sop_sections_hungary = [
    {
        "heading": "1. INTRODUCTION & ACADEMIC FOUNDATION",
        "paragraphs": [
            "My journey into advanced computing is founded upon a core conviction: the most reliable, fault-tolerant software systems are fundamentally rooted in rigorous mathematical principles. Having graduated with a Bachelor of Technology in Mathematics from Olusegun Agagu University of Science and Technology (OAUSTECH), specializing in Operations Research and Computational Mathematics, I approach software engineering not merely as the syntactic assembly of code, but as the deliberate formulation of deterministic finite-state automata, discrete optimization models, and graph-theoretical algorithms.",
            "Over the past five years, I have actively unified this rigorous mathematical background with large-scale production software engineering—architecting resilient cross-platform mobile systems, implementing zero-loss fintech payment transaction gateways, and managing decoupled cloud infrastructures. Under the prestigious Stipendium Hungaricum Scholarship Programme, I am applying for the Master of Science in Computer Science at Eötvös Loránd University (ELTE) as my first choice and the University of Debrecen as my second choice. My objective is to deepen my academic foundations in advanced distributed consensus, formal software verification, and high-performance concurrent architectures within Hungary's world-renowned informatics ecosystem."
        ]
    },
    {
        "heading": "2. BRIDGING COMPUTATIONAL MATHEMATICS & PRODUCTION ENGINEERING",
        "paragraphs": [
            "Throughout my undergraduate curriculum, advanced coursework in Numerical Analysis, Linear and Non-Linear Optimization, and Discrete Mathematics demonstrated that computational complexity directly governs real-world performance. Rather than designing software heuristically, I utilized mathematical frameworks to diagnose and eliminate bottlenecks across production applications.",
            "A concrete example arose when I engineered the real-time transaction engine for an e-commerce platform processing thousands of live transactions via the Paystack payment gateway. Under high concurrency and variable cellular latencies, standard asynchronous architectures risk race conditions and duplicate ledger postings. Applying transaction isolation theory, I engineered atomic row-level locks using select-for-update semantics at the database engine level and integrated cryptographic HMAC-SHA512 webhook signature verification. To guarantee zero data discrepancy, I designed an idempotent event-driven queueing pipeline with deterministic exponential backoff handlers. This mathematically sound design eliminated 100% of transaction state anomalies and maintained strict financial ledger consistency across unstable network conditions."
        ]
    },
    {
        "heading": "3. PROFESSIONAL EXPERIENCE & SYSTEMS ARCHITECTURE",
        "paragraphs": [
            "My industry progression has reinforced my capacity to design and maintain systems across the entire decoupled stack. Through my software engineering firm, EmpireCodes, I developed and published a comprehensive production mobile and web fleet. Utilizing React Native and Expo SDK, I engineered production mobile applications incorporating offline-first state reconciliation with asynchronous storage and synchronized audio-haptic micro-interactions. On the backend, I designed high-throughput RESTful APIs using Python and Django REST Framework, containerized with Docker and deployed across cloud microservices.",
            "Beyond building commercial products, I served as a Backend Developer and Technical Instructor at AnchorSoft Academy in Lagos, where I trained aspiring software engineers in relational database normalization, API security, and Python development. Furthermore, during my National Youth Service Corps (NYSC) deployment within the Procurement Unit of the Somolu Local Government Council (completed in 2026), I identified severe manual record-keeping bottlenecks and engineered an automated municipal budget tracking pipeline using Python and relational database schemas, reducing procurement processing turnaround by 40%."
        ]
    },
    {
        "heading": "4. WHY HUNGARY, ELTE, & CAREER OBJECTIVES",
        "paragraphs": [
            "Hungary has a celebrated global reputation in mathematics, algorithmics, and computer science—from the foundational contributions of John von Neumann, Paul Erdős, and László Lovász to today's cutting-edge informatics faculties. The Master of Science in Computer Science curriculum at Eötvös Loránd University (ELTE), Budapest, and the University of Debrecen represents the ideal intellectual bridge for my background.",
            "I am particularly drawn to ELTE's Faculty of Informatics and its specialized tracks in Software Technology and Distributed Systems, specifically research coursework covering Formal Methods, Advanced Algorithms, and Cloud-Native Distributed Computing. Having completed my undergraduate degree in an English-speaking higher education system with proven English proficiency, I am fully equipped to thrive within Hungary's international academic community.",
            "Following completion of my master's degree, my long-term objective is to operate as a Lead Systems Architect and Distributed Computing Researcher, contributing to mission-critical software infrastructure, advancing fintech security protocols, and fostering international technological partnerships between Europe and emerging technology ecosystems."
        ]
    },
    {
        "heading": "5. CONCLUSION",
        "paragraphs": [
            "I offer the Stipendium Hungaricum selection committee and the graduate faculty at Eötvös Loránd University and the University of Debrecen a proven union of rigorous undergraduate mathematical training, five years of verified full-stack production engineering, and an unyielding commitment to academic excellence. I am prepared to dedicate myself fully to the academic rigors of the programme and to represent the values of the Stipendium Hungaricum scholarship with distinction.",
            "Thank you for considering my application."
        ]
    }
]

sop_sections_general = [
    {
        "heading": "1. INTRODUCTION & ACADEMIC FOUNDATION",
        "paragraphs": [
            "My journey into advanced computing began with a foundational conviction: the most reliable, fault-tolerant software systems are rooted in mathematical principles. Having completed my Bachelor of Technology in Mathematics at Olusegun Agagu University of Science and Technology (OAUSTECH), specializing in Operations Research and Computational Mathematics, I approach software engineering not merely as the mechanics of writing syntax, but as the rigorous design of deterministic state machines, optimal graph algorithms, and constrained optimization models.",
            "Over the past five years, I have actively bridged this theoretical foundation with real-world production engineering—architecting cross-platform mobile applications, engineering zero-loss financial transaction gateways, and managing decoupled cloud infrastructures. I am now applying to the Master of Science in Computer Science / Software Engineering to deepen my mastery of advanced distributed systems, concurrent software architectures, and automated verification paradigms."
        ]
    },
    {
        "heading": "2. BRIDGING COMPUTATIONAL MATHEMATICS & PRODUCTION ENGINEERING",
        "paragraphs": [
            "During my undergraduate studies, courses in Numerical Analysis, Optimization Theory, and Discrete Mathematics revealed how computational complexity governs real-world computing. I applied this directly to my software engineering practice. Rather than building systems intuitively, I utilized mathematical principles to eliminate bottlenecks in production platforms.",
            "For example, when architecting the transactional pipeline for an e-commerce platform processing thousands of live payments via the Paystack gateway, I recognized that concurrency and network latency created high risks for duplicate ledger credits and state drift. Applying database transaction isolation theory, I implemented atomic row-level locks (SELECT FOR UPDATE) and cryptographic HMAC-SHA512 webhook signature verification. To ensure zero data discrepancy, I designed an idempotent event-driven queueing architecture with exponential backoff workers. This rigorous mathematical approach eliminated 100% of transaction race conditions and guaranteed ledger consistency across volatile network conditions."
        ]
    },
    {
        "heading": "3. PROFESSIONAL EXPERIENCE & LEADERSHIP",
        "paragraphs": [
            "My professional progression has reinforced my capacity to engineer systems across the entire decoupled stack. Under my software firm, EmpireCodes, I developed and published a tri-tier mobile and web fleet. Utilizing React Native and Expo SDK, I engineered production mobile applications incorporating offline-first state reconciliation with asynchronous storage and synchronized audio-haptic micro-interactions. On the backend, I designed high-throughput RESTful APIs using Python and Django REST Framework, containerized with Docker and deployed across cloud microservices.",
            "In addition to building commercial products, I served as a Backend Developer and Instructor at AnchorSoft Academy, where I mentored aspiring software engineers in relational database normalization, API security, and Python development. Furthermore, during my National Youth Service Corps (NYSC) deployment within the Procurement Unit of the Somolu Local Government Council (completed 2026), I identified severe manual record-keeping bottlenecks and engineered an automated municipal budget tracking pipeline using Python and relational database schemas, reducing procurement processing turnaround by 40%."
        ]
    },
    {
        "heading": "4. WHY THIS MASTER’S PROGRAM & CAREER OBJECTIVES",
        "paragraphs": [
            "While my industry experience has given me deep practical fluency with modern developer tools and frameworks, I recognize that solving next-generation engineering problems—such as large-scale distributed consensus, autonomous agent orchestration, and formal verification—demands advanced graduate research.",
            "Your Master of Science curriculum stands out as the ideal intellectual environment for my aspirations. I am particularly drawn to your department's curriculum in Distributed Systems, Concurrent Software Architecture, and Database Systems Optimization. The program's balance of rigorous theoretical foundations and applied engineering aligns directly with my goal of becoming a Lead Systems Architect capable of engineering resilient, high-volume infrastructure."
        ]
    },
    {
        "heading": "5. CONCLUSION",
        "paragraphs": [
            "I bring a unique blend of theoretical mathematical training, five years of verified production engineering experience, and a relentless drive for excellence. I am fully prepared to meet the academic and collaborative demands of your graduate faculty, and I look forward to contributing actively to your research community.",
            "Thank you for considering my application."
        ]
    }
]

if __name__ == '__main__':
    base_dir = r"c:\Users\PC\Downloads\empirecodes_edit_now\empirecodes"

    # 1. Stipendium Hungaricum Specific (Ready to upload right now!)
    hungary_pdf = os.path.join(base_dir, "Statement_of_Purpose_Stipendium_Hungaricum.pdf")
    build_pdf(
        hungary_pdf,
        "STATEMENT OF PURPOSE",
        "Master of Science (M.Sc.) in Computer Science",
        "Eötvös Loránd University (ELTE), Budapest (1st Choice) | University of Debrecen (2nd Choice)",
        sop_sections_hungary
    )

    hungary_docx = os.path.join(base_dir, "Statement_of_Purpose_Stipendium_Hungaricum.docx")
    create_docx(
        hungary_docx,
        "STATEMENT OF PURPOSE",
        "Anthony Oluwaseun Matthew",
        "Master of Science (M.Sc.) in Computer Science",
        "Eötvös Loránd University (ELTE), Budapest (1st Choice) | University of Debrecen (2nd Choice)",
        sop_sections_hungary
    )

    # 2. General Version (For Italy, Germany, and other European portals)
    general_pdf = os.path.join(base_dir, "Statement_of_Purpose_Anthony_Matthew.pdf")
    build_pdf(
        general_pdf,
        "STATEMENT OF PURPOSE",
        "Master of Science (M.Sc.) in Computer Science / Software Engineering",
        "[Target Institution, e.g., Politecnico di Milano / University of Bologna / University of Passau]",
        sop_sections_general
    )

    general_docx = os.path.join(base_dir, "Statement_of_Purpose_Anthony_Matthew.docx")
    create_docx(
        general_docx,
        "STATEMENT OF PURPOSE",
        "Anthony Oluwaseun Matthew",
        "Master of Science (M.Sc.) in Computer Science / Software Engineering",
        "[Target Institution, e.g., Politecnico di Milano / University of Bologna / University of Passau]",
        sop_sections_general
    )

    print("\nALL FILES CREATED SUCCESSFULLY!")

