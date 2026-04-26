"""
utils/pdf_report.py  —  Professional CKD Screening Report (ReportLab)
Clean two-column medical report layout.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, KeepTogether)

# ── Palette ────────────────────────────────────────────────────────────────────
C_NAVY   = colors.HexColor("#0D1B2A")
C_BLUE   = colors.HexColor("#1565C0")
C_CYAN   = colors.HexColor("#0097A7")
C_GREEN  = colors.HexColor("#2E7D32")
C_ORANGE = colors.HexColor("#E65100")
C_RED    = colors.HexColor("#C62828")
C_GREY   = colors.HexColor("#455A64")
C_LGREY  = colors.HexColor("#ECEFF1")
C_WHITE  = colors.white
C_STRIPE = colors.HexColor("#F5F9FF")

PAGE_W   = A4[0] - 4*cm          # usable width

def _risk_colour(level: str):
    return {
        "Low Risk"      : C_GREEN,
        "Moderate Risk" : C_ORANGE,
        "High Risk"     : C_RED,
    }.get(level, C_GREY)

# ── Paragraph styles ───────────────────────────────────────────────────────────
def _S(name, **kw) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=9, textColor=C_NAVY,
                leading=13, spaceAfter=2)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    "h1"     : _S("h1", fontName="Helvetica-Bold", fontSize=18,
                  textColor=C_WHITE, alignment=TA_CENTER, leading=22),
    "h1sub"  : _S("h1sub", fontSize=9, textColor=colors.HexColor("#B0C4D8"),
                  alignment=TA_CENTER),
    "sec"    : _S("sec", fontName="Helvetica-Bold", fontSize=10,
                  textColor=C_BLUE, spaceBefore=8, spaceAfter=3, leading=14),
    "label"  : _S("lbl", fontName="Helvetica-Bold", fontSize=8,
                  textColor=C_GREY),
    "value"  : _S("val", fontSize=9, textColor=C_NAVY),
    "body"   : _S("body", fontSize=9, textColor=C_NAVY, leading=14),
    "italic" : _S("it",   fontName="Helvetica-Oblique", fontSize=9.5,
                  textColor=C_NAVY, leading=15),
    "small"  : _S("sm",   fontSize=7.5, textColor=C_GREY, leading=10),
    "disc"   : _S("disc", fontName="Helvetica-Oblique", fontSize=7.5,
                  textColor=C_GREY, leading=11, alignment=TA_JUSTIFY),
    "bold9"  : _S("b9",  fontName="Helvetica-Bold", fontSize=9, textColor=C_NAVY),
    "center" : _S("ctr", alignment=TA_CENTER),
    "bignum" : _S("big", fontName="Helvetica-Bold", fontSize=30,
                  alignment=TA_CENTER, textColor=C_WHITE, leading=34),
    "biglbl" : _S("bigl", fontSize=8, alignment=TA_CENTER,
                  textColor=colors.HexColor("#B0C4D8"), leading=10),
    "risklbl": _S("rl",  fontName="Helvetica-Bold", fontSize=14,
                  alignment=TA_CENTER, leading=18),
    "footer" : _S("ft",  fontSize=7, textColor=C_GREY, alignment=TA_CENTER, leading=10),
}

# ── Table style helpers ────────────────────────────────────────────────────────
def _TS(*cmds) -> TableStyle:
    base = [
        ("FONTSIZE",    (0,0),(-1,-1), 8.5),
        ("TOPPADDING",  (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0),(-1,-1), 7),
        ("RIGHTPADDING",(0,0),(-1,-1), 7),
        ("VALIGN",      (0,0),(-1,-1), "MIDDLE"),
    ]
    return TableStyle(base + list(cmds))

def _header_style() -> TableStyle:
    return _TS(
        ("BACKGROUND",   (0,0),(-1,0), C_NAVY),
        ("TEXTCOLOR",    (0,0),(-1,0), C_WHITE),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [C_WHITE, C_STRIPE]),
        ("GRID",         (0,0),(-1,-1), 0.3, colors.HexColor("#CFD8DC")),
    )

# ── Section divider ────────────────────────────────────────────────────────────
def _section(title: str) -> list:
    return [
        Spacer(1, 6),
        Paragraph(title, S["sec"]),
        HRFlowable(width="100%", thickness=0.8, color=C_CYAN, spaceAfter=4),
    ]

# ── Main PDF builder ───────────────────────────────────────────────────────────
def generate_pdf(result: dict, patient_data: dict,
                 user_info: dict, hospitals: list) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.8*cm, bottomMargin=2*cm,
        title="CKD Screening Report"
    )
    story = []

    prob   = result.get("risk_percent", 0)
    risk   = result.get("risk_level",   "Unknown")
    stage  = result.get("stage",        "N/A")
    expl   = result.get("explanation_text", "")
    rec    = result.get("recommendation",   "")
    rclr   = _risk_colour(risk)
    now    = datetime.now().strftime("%d %B %Y, %H:%M")
    stage_short = stage.split("–")[0].strip() if "–" in stage else stage

    # ── 1. HEADER BANNER ───────────────────────────────────────────────────────
    hdr = Table([[
        Paragraph("CKD Early Diagnosis System", S["h1"]),
    ]], colWidths=[PAGE_W])
    hdr.setStyle(_TS(
        ("BACKGROUND",   (0,0),(-1,-1), C_NAVY),
        ("TOPPADDING",   (0,0),(-1,-1), 14),
        ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ("ROUNDEDCORNERS",(0,0),(-1,-1),[6,6,6,6]),
    ))
    story += [hdr,
              Table([[Paragraph(f"AI-Powered Screening Report  |  Generated: {now}", S["h1sub"])]],
                    colWidths=[PAGE_W],
                    style=_TS(("BACKGROUND",(0,0),(-1,-1),C_NAVY),
                              ("BOTTOMPADDING",(0,0),(-1,-1),10),
                              ("ROUNDEDCORNERS",(0,0),(-1,-1),[0,0,6,6]))),
              Spacer(1, 8)]

    # ── 2. RISK SUMMARY BANNER ─────────────────────────────────────────────────
    risk_tbl = Table([
        [Paragraph(f"{prob}%",       S["bignum"]),
         Paragraph(risk,             ParagraphStyle("rsk", fontName="Helvetica-Bold",
                                                    fontSize=18, textColor=rclr,
                                                    alignment=TA_CENTER, leading=22)),
         Paragraph(stage_short,      ParagraphStyle("stg", fontName="Helvetica-Bold",
                                                    fontSize=11, textColor=C_CYAN,
                                                    alignment=TA_CENTER, leading=14))],
        [Paragraph("CKD Risk Probability", S["biglbl"]),
         Paragraph("Risk Category",        S["biglbl"]),
         Paragraph("CKD Stage",            S["biglbl"])],
    ], colWidths=[PAGE_W/3]*3)
    risk_tbl.setStyle(_TS(
        ("BACKGROUND",    (0,0),(-1,-1), C_NAVY),
        ("ROUNDEDCORNERS",(0,0),(-1,-1), [6,6,6,6]),
        ("LINEABOVE",     (1,0),(1,0), 3, rclr),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LINEABOVE",     (0,0),(-1,0), 3, rclr),
    ))
    story += [risk_tbl, Spacer(1, 10)]

    # ── 3. PATIENT INFO ────────────────────────────────────────────────────────
    story += _section("PATIENT INFORMATION")
    info_rows = [
        [Paragraph("<b>Patient Name</b>",   S["label"]),
         Paragraph(user_info.get("patient_name","N/A"), S["value"]),
         Paragraph("<b>Age / Gender</b>",   S["label"]),
         Paragraph(f"{user_info.get('age','N/A')} yrs / {user_info.get('gender','N/A')}", S["value"])],
        [Paragraph("<b>Email</b>",          S["label"]),
         Paragraph(user_info.get("email","N/A"),        S["value"]),
         Paragraph("<b>Contact</b>",        S["label"]),
         Paragraph(user_info.get("contact","N/A"),      S["value"])],
        [Paragraph("<b>Blood Group</b>",    S["label"]),
         Paragraph(user_info.get("blood_group","N/A"),  S["value"]),
         Paragraph("<b>City / State</b>",   S["label"]),
         Paragraph(f"{user_info.get('city','N/A')} / {user_info.get('state','N/A')}", S["value"])],
        [Paragraph("<b>Address</b>",        S["label"]),
         Paragraph(user_info.get("address","N/A"),      S["value"]),
         Paragraph("<b>PIN Code</b>",       S["label"]),
         Paragraph(user_info.get("pin","N/A"),          S["value"])],
    ]
    info_tbl = Table(info_rows, colWidths=[3.2*cm, 5.5*cm, 3.2*cm, 5.5*cm])
    info_tbl.setStyle(_TS(
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_STRIPE, C_WHITE]),
        ("GRID",         (0,0),(-1,-1), 0.3, colors.HexColor("#CFD8DC")),
        ("FONTNAME",     (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",     (2,0),(2,-1), "Helvetica-Bold"),
    ))
    story += [info_tbl, Spacer(1, 4)]

    # ── 4. AI EXPLANATION ──────────────────────────────────────────────────────
    story += _section("AI EXPLANATION  (Explainable AI Insight)")
    expl_tbl = Table([[Paragraph(f'"{expl}"', S["italic"])]], colWidths=[PAGE_W])
    expl_tbl.setStyle(_TS(
        ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#E3F2FD")),
        ("LINEBEFORE",  (0,0),(0,-1), 4, C_CYAN),
        ("TOPPADDING",  (0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING", (0,0),(-1,-1), 12),
    ))
    story += [expl_tbl, Spacer(1, 4)]

    # Stage detail
    story.append(Paragraph(f"<b>Stage Detail:</b>  {stage}", S["body"]))

    # ── 5. LAB PARAMETERS (2-column grid) ─────────────────────────────────────
    story += _section("INPUT LAB PARAMETERS")
    params = [
        ("Age",               f"{patient_data.get('Age','')} yrs"),
        ("Blood Pressure",    f"{patient_data.get('BloodPressure','')} mmHg"),
        ("Serum Creatinine",  f"{patient_data.get('SerumCreatinine','')} mg/dL"),
        ("Hemoglobin",        f"{patient_data.get('Hemoglobin','')} g/dL"),
        ("Blood Urea",        f"{patient_data.get('BloodUrea','')} mg/dL"),
        ("Blood Glucose",     f"{patient_data.get('BloodGlucose','')} mg/dL"),
        ("Sodium",            f"{patient_data.get('Sodium','')} mEq/L"),
        ("Potassium",         f"{patient_data.get('Potassium','')} mEq/L"),
        ("WBC Count",         f"{patient_data.get('WBCCount','')} /uL"),
        ("RBC Count",         f"{patient_data.get('RBCCount','')} M/uL"),
        ("Packed Cell Volume",f"{patient_data.get('PackedCellVolume','')} %"),
        ("Albumin",           str(patient_data.get('Albumin',''))),
        ("Specific Gravity",  str(patient_data.get('SpecificGravity',''))),
        ("Hypertension",      str(patient_data.get('Hypertension',''))),
        ("Diabetes",          str(patient_data.get('DiabetesMellitus',''))),
        ("Anemia",            str(patient_data.get('Anemia',''))),
        ("Appetite",          str(patient_data.get('Appetite',''))),
        ("Pedal Edema",       str(patient_data.get('PedalEdema',''))),
    ]
    lab_rows = []
    for i in range(0, len(params), 2):
        a = params[i]
        b = params[i+1] if i+1 < len(params) else ("","")
        lab_rows.append([
            Paragraph(a[0], S["label"]), Paragraph(a[1], S["value"]),
            Paragraph(b[0], S["label"]), Paragraph(b[1], S["value"]),
        ])
    lab_tbl = Table(lab_rows, colWidths=[4*cm, 4.5*cm, 4*cm, 4.9*cm])
    lab_tbl.setStyle(_TS(
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[C_STRIPE, C_WHITE]),
        ("GRID",         (0,0),(-1,-1), 0.3, colors.HexColor("#CFD8DC")),
    ))
    story += [lab_tbl, Spacer(1, 4)]

    # ── 6. CLINICAL RECOMMENDATION ────────────────────────────────────────────
    story += _section("CLINICAL RECOMMENDATION")
    rec_lines = [l.strip() for l in rec.split("\n") if l.strip()]
    rec_rows  = [[Paragraph(line, S["body"])] for line in rec_lines]
    rec_tbl   = Table(rec_rows, colWidths=[PAGE_W])
    rec_tbl.setStyle(_TS(
        ("BACKGROUND",  (0,0),(-1,-1), colors.HexColor("#FFF8E1")),
        ("LINEBEFORE",  (0,0),(0,-1), 4, C_ORANGE if risk=="Moderate Risk"
                                         else C_RED if risk=="High Risk" else C_GREEN),
        ("LEFTPADDING", (0,0),(-1,-1), 12),
        ("GRID",        (0,0),(-1,-1), 0.3, colors.HexColor("#FFE082")),
    ))
    story += [rec_tbl, Spacer(1, 4)]

    # ── 7. HOSPITALS ───────────────────────────────────────────────────────────
    if hospitals:
        story += _section("RECOMMENDED NEPHROLOGY CENTRES")
        h_header = [Paragraph(h, ParagraphStyle("hh",fontName="Helvetica-Bold",
                                                 fontSize=8,textColor=C_WHITE))
                    for h in ["Hospital", "City / State", "Address", "Phone", "Specialty", "Type", "Rating"]]
        h_data   = [h_header]
        for h in hospitals[:6]:
            stars = "★" * int(float(h.get("Rating",0)))
            h_data.append([
                Paragraph(h.get("Hospital Name",""),  S["bold9"]),
                Paragraph(f"{h.get('City','')} / {h.get('State','')}", S["small"]),
                Paragraph(h.get("Address",""),         S["small"]),
                Paragraph(h.get("Phone",""),           S["small"]),
                Paragraph(h.get("Specialty",""),       S["small"]),
                Paragraph(h.get("Type",""),            S["small"]),
                Paragraph(f"{stars} {h.get('Rating','')}",S["small"]),
            ])
        h_tbl = Table(h_data, colWidths=[3.5*cm,2.8*cm,4.0*cm,2.1*cm,2.5*cm,1.8*cm,1.3*cm])
        h_tbl.setStyle(_header_style())
        story += [h_tbl, Spacer(1, 6)]

    # ── 8. FOOTER ──────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=C_NAVY, spaceAfter=5))
    priv = Table([[
        Paragraph("<b>Data Privacy:</b>  All patient data is processed locally. "
                  "No data is transmitted to external servers.", S["disc"]),
        Paragraph("<b>DISCLAIMER:</b>  This report is for preliminary screening only "
                  "and does NOT replace professional medical diagnosis. Consult a "
                  "qualified nephrologist for clinical decisions.", S["disc"]),
    ]], colWidths=[PAGE_W*0.48, PAGE_W*0.52])
    priv.setStyle(_TS(
        ("BACKGROUND",(0,0),(-1,-1),C_LGREY),
        ("VALIGN",    (0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),
    ))
    story.append(priv)
    story.append(Spacer(1,4))
    story.append(Paragraph(
        f"CKD Early Diagnosis System  |  Final Year AI/ML Project  |  "
        f"Powered by Machine Learning + Explainable AI  |  {datetime.now().year}",
        S["footer"]))

    doc.build(story)
    buf.seek(0)
    return buf.read()
