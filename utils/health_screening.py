"""
utils/health_screening.py
Rule-based multi-condition health screening engine.
Runs AFTER the CKD ML prediction using the same patient inputs.
Returns a list of Finding objects — one per health domain.
"""

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Finding:
    condition   : str                # e.g. "Diabetes Risk"
    status      : str                # e.g. "High Risk", "Normal", "Elevated"
    severity    : str                # "critical" | "warning" | "normal"
    icon        : str                # emoji for UI
    color       : str                # hex color
    parameters  : list               # [{"name": "BloodGlucose", "value": 126, "unit": "mg/dL", "flag": "HIGH"}]
    explanation : str                # plain-English explanation of the condition
    triggered_by: str                # which parameter(s) caused this finding
    recommendation: str             # clinical action advice


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _sev_color(severity: str) -> str:
    return {"critical": "#FF3B5C", "warning": "#FF8C42", "normal": "#00E5A0"}.get(severity, "#7A9CC0")

def _sev_icon(severity: str) -> str:
    return {"critical": "🔴", "warning": "🟡", "normal": "🟢"}.get(severity, "⚪")

def _flag(value, low=None, high=None):
    """Return 'HIGH', 'LOW', or 'NORMAL' badge for a numeric parameter."""
    if high is not None and value > high:
        return "HIGH"
    if low is not None and value < low:
        return "LOW"
    return "NORMAL"


# ─────────────────────────────────────────────────────────────────────────────
# Individual detector functions
# ─────────────────────────────────────────────────────────────────────────────

def detect_diabetes(bg: float, sugar: int) -> Finding:
    """
    Parameters: BloodGlucose (fasting, mg/dL), Sugar (urine dipstick 0-5)
    """
    params = [
        {"name": "Blood Glucose",   "value": bg,    "unit": "mg/dL", "flag": _flag(bg, high=125)},
        {"name": "Urine Sugar",     "value": sugar,  "unit": "scale (0-5)", "flag": _flag(sugar, high=0)},
    ]

    if bg > 200:
        status = "Diabetes — Very High Glucose"
        severity = "critical"
        triggered = f"Blood Glucose critically elevated at {bg} mg/dL (normal fasting < 100)"
        explanation = (
            "Fasting blood glucose above 200 mg/dL is strongly indicative of diabetes mellitus. "
            "At this level, the body is unable to regulate blood sugar adequately, which can cause "
            "serious damage to kidneys, eyes, nerves, and blood vessels if left unmanaged."
        )
        rec = (
            "⚠️ URGENT: Consult an endocrinologist or diabetologist immediately.\n"
            "• Confirm with HbA1c test and repeat fasting glucose.\n"
            "• Start dietary changes: low glycemic index foods, reduce refined carbs & sugar.\n"
            "• Regular blood glucose monitoring (fasting + post-meal).\n"
            "• Discuss medication (metformin or insulin) with your doctor.\n"
            "• Note: Diabetes is a major accelerator of CKD progression."
        )
    elif bg > 126:
        status = "Diabetes Risk — High"
        severity = "critical"
        triggered = f"Blood Glucose {bg} mg/dL exceeds diabetic threshold of 126 mg/dL"
        explanation = (
            "Fasting blood glucose ≥ 126 mg/dL meets the clinical threshold for diabetes mellitus "
            "diagnosis (ADA guidelines). Persistently elevated glucose damages the tiny blood vessels "
            "in the kidneys (glomeruli), leading to diabetic nephropathy — the leading cause of CKD."
        )
        rec = (
            "• Confirm diagnosis with a second fasting glucose or HbA1c test.\n"
            "• Consult an endocrinologist for a personalised diabetes management plan.\n"
            "• Adopt a low-sugar, low-GI diet; aim for 30 min moderate exercise daily.\n"
            "• Monitor blood pressure — diabetes + hypertension doubles kidney risk.\n"
            "• Schedule kidney function tests (eGFR, urine albumin) every 6 months."
        )
    elif bg >= 100:
        status = "Prediabetes — Elevated"
        severity = "warning"
        triggered = f"Blood Glucose {bg} mg/dL is in the prediabetes range (100–125 mg/dL)"
        explanation = (
            "Fasting glucose between 100–125 mg/dL indicates prediabetes (Impaired Fasting Glucose). "
            "This is a reversible stage where the body is becoming resistant to insulin. "
            "Without lifestyle changes, prediabetes often progresses to type 2 diabetes within 10 years."
        )
        rec = (
            "• Lifestyle intervention is highly effective at this stage.\n"
            "• Reduce intake of refined carbohydrates, sugary beverages, and processed foods.\n"
            "• Target at least 150 minutes of moderate aerobic activity per week.\n"
            "• Lose 5–10% of body weight if overweight.\n"
            "• Retest fasting glucose every 6–12 months.\n"
            "• Consult your doctor about metformin if multiple risk factors are present."
        )
    else:
        status = "Normal"
        severity = "normal"
        triggered = f"Blood Glucose {bg} mg/dL is within normal fasting range (< 100 mg/dL)"
        explanation = (
            "Fasting blood glucose is within the normal range. The body is regulating blood sugar "
            "effectively. Continue healthy dietary habits and screen annually if there is a family "
            "history of diabetes."
        )
        rec = (
            "• Maintain a balanced diet low in refined sugars and processed foods.\n"
            "• Stay physically active with regular exercise.\n"
            "• Annual fasting glucose screening is recommended for adults over 40."
        )

    # Elevate severity if urine sugar is also abnormal
    if sugar > 0 and severity == "normal":
        severity = "warning"
        status = "Glycosuria Noted"
        triggered += f"; Urine sugar also positive (score: {sugar})"

    return Finding(
        condition="Diabetes Risk",
        status=status,
        severity=severity,
        icon="🍬",
        color=_sev_color(severity),
        parameters=params,
        explanation=explanation,
        triggered_by=triggered,
        recommendation=rec,
    )


def detect_hypertension(bp: float) -> Finding:
    params = [
        {"name": "Blood Pressure (Systolic)", "value": bp, "unit": "mmHg",
         "flag": _flag(bp, high=119)},
    ]

    if bp >= 180:
        status = "Hypertensive Crisis"
        severity = "critical"
        triggered = f"Blood Pressure {bp} mmHg — hypertensive crisis (≥ 180 mmHg)"
        explanation = (
            "A systolic blood pressure of 180 mmHg or above is a hypertensive crisis requiring "
            "immediate medical evaluation. At these levels, blood vessels are under extreme stress, "
            "dramatically increasing the risk of stroke, heart attack, kidney failure, and organ damage."
        )
        rec = (
            "🚨 SEEK EMERGENCY CARE immediately if BP is consistently ≥ 180 mmHg.\n"
            "• Do not wait — call emergency services or go to the nearest hospital.\n"
            "• Avoid strenuous activity; remain calm and seated.\n"
            "• If on antihypertensive medications, take your prescribed dose.\n"
            "• Hypertension is the second leading cause of CKD — aggressive control is essential."
        )
    elif bp >= 140:
        status = "High Blood Pressure (Stage 2)"
        severity = "critical"
        triggered = f"Blood Pressure {bp} mmHg meets Stage 2 Hypertension criteria (≥ 140 mmHg)"
        explanation = (
            "Stage 2 hypertension (systolic ≥ 140 mmHg) places sustained high pressure on kidney "
            "blood vessels, damaging the glomerular filtration system over time. "
            "Hypertension is both a cause and a consequence of CKD, creating a dangerous cycle."
        )
        rec = (
            "• Consult a cardiologist or internist promptly.\n"
            "• Begin or review antihypertensive medication (ACE inhibitors/ARBs are kidney-protective).\n"
            "• Restrict sodium intake to < 1500 mg/day.\n"
            "• Follow DASH diet: fruits, vegetables, low-fat dairy, reduced saturated fat.\n"
            "• Monitor blood pressure at home twice daily.\n"
            "• Target: < 130/80 mmHg for CKD patients."
        )
    elif bp >= 130:
        status = "High Blood Pressure (Stage 1)"
        severity = "warning"
        triggered = f"Blood Pressure {bp} mmHg is Stage 1 Hypertension (130–139 mmHg)"
        explanation = (
            "Stage 1 hypertension (130–139 mmHg) increases the risk of cardiovascular disease "
            "and can accelerate kidney damage. At this stage, lifestyle changes alone may be "
            "sufficient for many patients, though some will need medication."
        )
        rec = (
            "• Discuss blood pressure medication with your doctor.\n"
            "• Adopt a low-sodium diet (< 2000 mg/day).\n"
            "• Limit alcohol and quit smoking.\n"
            "• Exercise at least 30 minutes most days.\n"
            "• Monitor BP every 1–3 months."
        )
    elif bp >= 120:
        status = "Elevated Blood Pressure"
        severity = "warning"
        triggered = f"Blood Pressure {bp} mmHg is elevated (120–129 mmHg)"
        explanation = (
            "Elevated blood pressure (120–129 mmHg) is above the optimal range but does not yet "
            "meet the Stage 1 hypertension threshold. Without lifestyle changes, this commonly "
            "progresses to hypertension within a few years."
        )
        rec = (
            "• Reduce sodium intake and increase potassium-rich foods (if kidneys allow).\n"
            "• Achieve or maintain a healthy body weight (BMI 18.5–24.9).\n"
            "• Limit caffeine and alcohol consumption.\n"
            "• Recheck blood pressure in 3–6 months."
        )
    else:
        status = "Normal"
        severity = "normal"
        triggered = f"Blood Pressure {bp} mmHg is within the normal range (< 120 mmHg)"
        explanation = (
            "Blood pressure is within the healthy normal range. Maintaining this protects both "
            "heart and kidneys from pressure-related damage."
        )
        rec = (
            "• Continue healthy lifestyle habits.\n"
            "• Annual blood pressure screening is recommended.\n"
            "• Maintain a low-sodium, balanced diet and regular physical activity."
        )

    return Finding(
        condition="Hypertension",
        status=status,
        severity=severity,
        icon="💉",
        color=_sev_color(severity),
        parameters=params,
        explanation=explanation,
        triggered_by=triggered,
        recommendation=rec,
    )


def detect_anemia(hgb: float, rbc: float, pcv: float) -> Finding:
    params = [
        {"name": "Hemoglobin",        "value": hgb, "unit": "g/dL",          "flag": _flag(hgb, low=12.0)},
        {"name": "RBC Count",         "value": rbc, "unit": "million/μL",     "flag": _flag(rbc, low=3.5)},
        {"name": "Packed Cell Volume","value": pcv, "unit": "%",              "flag": _flag(pcv, low=35)},
    ]
    triggers = []
    if hgb < 8.0:
        severity = "critical"
        status = "Severe Anemia"
        triggers.append(f"Hemoglobin critically low at {hgb} g/dL (severe anemia < 8.0)")
        explanation = (
            "Hemoglobin below 8.0 g/dL represents severe anemia. The blood can no longer carry "
            "enough oxygen to vital organs. In CKD, severe anemia results from the kidneys' failure "
            "to produce erythropoietin (EPO), the hormone that stimulates red blood cell production. "
            "This causes extreme fatigue, shortness of breath, and cardiac stress."
        )
        rec = (
            "🚨 Urgent nephrology review required.\n"
            "• Blood transfusion may be necessary.\n"
            "• EPO-stimulating agents (ESA therapy) should be evaluated.\n"
            "• Check iron stores (serum ferritin, transferrin saturation).\n"
            "• Assess for gastrointestinal bleeding as a contributing cause.\n"
            "• Iron supplementation (IV iron preferred in CKD)."
        )
    elif hgb < 12.0:
        severity = "warning"
        status = "Anemia Risk"
        triggers.append(f"Hemoglobin {hgb} g/dL below normal threshold of 12.0 g/dL")
        explanation = (
            "Hemoglobin below 12 g/dL indicates anemia. In the context of CKD, this is commonly "
            "renal anemia — caused by reduced erythropoietin production as kidney function declines. "
            "Symptoms include fatigue, pallor, shortness of breath on exertion, and poor concentration."
        )
        rec = (
            "• Consult a nephrologist or hematologist for anemia evaluation.\n"
            "• Check: serum iron, TIBC, ferritin, B12, folate, reticulocyte count.\n"
            "• If iron-deficient: oral or IV iron supplementation.\n"
            "• If EPO-deficient (renal anemia): discuss ESA therapy with nephrologist.\n"
            "• Avoid foods that inhibit iron absorption (tea, coffee) with iron supplements.\n"
            "• Eat iron-rich foods: spinach, egg yolks, fortified cereals (in permitted quantities)."
        )
    else:
        severity = "normal"
        status = "Normal"
        triggers.append(f"Hemoglobin {hgb} g/dL is within normal range (≥ 12 g/dL)")
        explanation = (
            "Hemoglobin and red blood cell indices are within the normal range, suggesting "
            "adequate oxygen-carrying capacity. Continue monitoring, especially if CKD is present, "
            "as anemia can develop as kidney function declines."
        )
        rec = (
            "• Continue a diet rich in iron, B12, and folate.\n"
            "• Annual CBC monitoring is recommended for patients with CKD risk factors."
        )

    if rbc < 3.5 and "RBC" not in str(triggers):
        triggers.append(f"RBC Count low at {rbc} million/μL")
    if pcv < 35 and "PCV" not in str(triggers):
        triggers.append(f"Packed Cell Volume low at {pcv}%")

    return Finding(
        condition="Anemia",
        status=status,
        severity=severity,
        icon="🩸",
        color=_sev_color(severity),
        parameters=params,
        explanation=explanation,
        triggered_by="; ".join(triggers) if triggers else f"All CBC values normal",
        recommendation=rec,
    )


def detect_uti(wbc: float, pus_cells: str, bacteria: str) -> Finding:
    bacteria_present = bacteria.lower() in ("present", "yes", "true", "1")
    pus_abnormal     = pus_cells.lower() in ("abnormal", "high", "yes", "present")

    params = [
        {"name": "WBC Count",  "value": wbc,      "unit": "/μL",
         "flag": _flag(wbc, high=11000)},
        {"name": "Pus Cells",  "value": pus_cells, "unit": "flag",
         "flag": "HIGH" if pus_abnormal else "NORMAL"},
        {"name": "Bacteria",   "value": bacteria,  "unit": "flag",
         "flag": "PRESENT" if bacteria_present else "ABSENT"},
    ]

    triggers = []
    score = 0
    if wbc > 15000:
        score += 2
        triggers.append(f"WBC Count markedly elevated at {wbc}/μL (suggests active infection)")
    elif wbc > 11000:
        score += 1
        triggers.append(f"WBC Count elevated at {wbc}/μL (normal < 11,000/μL)")
    if pus_abnormal:
        score += 2
        triggers.append("Abnormal pus cells in urine (pyuria — a hallmark of UTI)")
    if bacteria_present:
        score += 2
        triggers.append("Bacteria detected in urine (bacteriuria)")

    if score >= 4:
        status = "Likely Urinary Tract Infection"
        severity = "critical"
        explanation = (
            "Multiple markers strongly suggest an active urinary tract infection (UTI). "
            "The combination of elevated WBC (leukocytosis), pus cells in urine (pyuria), "
            "and bacteria in urine (bacteriuria) is the classic triad for UTI diagnosis. "
            "In patients with CKD, UTIs can rapidly worsen kidney function and must be treated promptly."
        )
        rec = (
            "⚠️ Consult a doctor promptly for urine culture and sensitivity testing.\n"
            "• Start antibiotic therapy as directed by your physician (culture-guided).\n"
            "• Increase fluid intake to help flush bacteria (if not fluid-restricted).\n"
            "• Complete the full antibiotic course — incomplete treatment leads to resistance.\n"
            "• In CKD patients: dose adjustments for antibiotics are often required.\n"
            "• Follow up with repeat urinalysis after treatment to confirm clearance."
        )
    elif score >= 2:
        status = "Possible Urinary Tract Infection"
        severity = "warning"
        explanation = (
            "Some markers suggest a possible urinary tract infection. Elevated white blood cells "
            "or pus cells in urine can indicate inflammation or early infection. This may also "
            "reflect sterile pyuria (inflammation without bacterial infection) in CKD patients."
        )
        rec = (
            "• Urine culture and microscopy are recommended to confirm or rule out UTI.\n"
            "• Monitor for UTI symptoms: burning urination, frequency, lower abdominal pain, fever.\n"
            "• Maintain good hydration (within any prescribed fluid limits).\n"
            "• Avoid delaying treatment — UTIs can escalate to pyelonephritis in CKD patients."
        )
    else:
        status = "No Infection Markers"
        severity = "normal"
        explanation = (
            "No significant markers of urinary tract infection detected. "
            "White blood cell count, pus cells, and bacteria are within acceptable ranges."
        )
        rec = (
            "• Maintain good hygiene practices to prevent UTIs.\n"
            "• Stay well-hydrated.\n"
            "• Report any urinary symptoms (burning, frequency, cloudy urine) to your doctor promptly."
        )

    return Finding(
        condition="Urinary Tract Infection",
        status=status,
        severity=severity,
        icon="🦠",
        color=_sev_color(severity),
        parameters=params,
        explanation=explanation,
        triggered_by="; ".join(triggers) if triggers else "No significant infection markers detected",
        recommendation=rec,
    )


def detect_electrolyte_imbalance(sodium: float, potassium: float) -> Finding:
    params = [
        {"name": "Sodium",    "value": sodium,    "unit": "mEq/L", "flag": _flag(sodium,    low=135, high=145)},
        {"name": "Potassium", "value": potassium, "unit": "mEq/L", "flag": _flag(potassium, low=3.5, high=5.0)},
    ]
    issues = []
    severity_rank = 0  # 0=normal, 1=warning, 2=critical

    # Potassium checks
    if potassium > 6.5:
        issues.append(("Severe Hyperkalemia", "critical",
                        f"Potassium critically high at {potassium} mEq/L (life-threatening > 6.5)",
                        "Potassium above 6.5 mEq/L is life-threatening. It disrupts the heart's electrical "
                        "conduction system, causing dangerous arrhythmias including ventricular fibrillation. "
                        "This is a common and dangerous complication in advanced CKD."))
        severity_rank = 2
    elif potassium > 5.5:
        issues.append(("Hyperkalemia", "critical",
                        f"Potassium elevated at {potassium} mEq/L (normal 3.5–5.0 mEq/L)",
                        "Hyperkalemia (potassium > 5.5 mEq/L) is a dangerous electrolyte disorder common in CKD. "
                        "Impaired kidneys cannot excrete potassium adequately, causing it to build up in the blood. "
                        "This can cause muscle weakness, heart palpitations, and life-threatening cardiac arrhythmias."))
        severity_rank = max(severity_rank, 2)
    elif potassium > 5.0:
        issues.append(("Mild Hyperkalemia", "warning",
                        f"Potassium mildly elevated at {potassium} mEq/L",
                        "Mildly elevated potassium needs monitoring, especially in CKD patients where "
                        "potassium regulation is compromised."))
        severity_rank = max(severity_rank, 1)
    elif potassium < 3.0:
        issues.append(("Severe Hypokalemia", "critical",
                        f"Potassium critically low at {potassium} mEq/L",
                        "Severe hypokalemia can cause dangerous cardiac arrhythmias and muscle paralysis."))
        severity_rank = max(severity_rank, 2)
    elif potassium < 3.5:
        issues.append(("Hypokalemia", "warning",
                        f"Potassium low at {potassium} mEq/L (normal 3.5–5.0)",
                        "Low potassium can cause muscle weakness, cramps, and heart rhythm disturbances."))
        severity_rank = max(severity_rank, 1)

    # Sodium checks
    if sodium < 125:
        issues.append(("Severe Hyponatremia", "critical",
                        f"Sodium critically low at {sodium} mEq/L",
                        "Severe hyponatremia can cause brain swelling, seizures, and coma."))
        severity_rank = max(severity_rank, 2)
    elif sodium < 135:
        issues.append(("Hyponatremia", "warning",
                        f"Sodium low at {sodium} mEq/L (normal 135–145 mEq/L)",
                        "Hyponatremia indicates dilutional or depletional sodium loss, which can cause "
                        "confusion, nausea, headaches, and in severe cases neurological complications. "
                        "In CKD, this may result from fluid retention or impaired renal regulation."))
        severity_rank = max(severity_rank, 1)
    elif sodium > 150:
        issues.append(("Hypernatremia", "warning",
                        f"Sodium elevated at {sodium} mEq/L (normal 135–145 mEq/L)",
                        "High sodium often indicates dehydration or excess salt intake."))
        severity_rank = max(severity_rank, 1)

    if not issues:
        return Finding(
            condition="Electrolyte Balance",
            status="Normal",
            severity="normal",
            icon="⚗️",
            color=_sev_color("normal"),
            parameters=params,
            explanation=(
                "Sodium and potassium levels are within normal physiological ranges. "
                "Electrolyte balance is essential for proper heart rhythm, muscle function, "
                "and fluid regulation."
            ),
            triggered_by=f"Sodium {sodium} mEq/L and Potassium {potassium} mEq/L are both normal",
            recommendation=(
                "• Maintain a balanced diet.\n"
                "• In CKD patients: monitor electrolytes every 3–6 months as kidney function changes.\n"
                "• Avoid excess salt and high-potassium foods as a preventive measure."
            ),
        )

    # Consolidate multiple issues
    all_names   = " + ".join(i[0] for i in issues)
    combined_sev = "critical" if severity_rank == 2 else "warning"
    combined_exp = " | ".join(i[3] for i in issues)
    all_triggers = "; ".join(i[2] for i in issues)

    rec_parts = []
    for name, _, _, _ in issues:
        if "Hyperkalemia" in name:
            rec_parts += [
                "• URGENT: Restrict high-potassium foods (banana, potato, tomato, nuts, dairy).",
                "• Discuss potassium binders (e.g., patiromer, sodium zirconium cyclosilicate) with your nephrologist.",
                "• Avoid NSAIDs, ACE inhibitors, or potassium-sparing diuretics unless prescribed.",
                "• Immediate ECG evaluation if potassium > 6.0 mEq/L.",
            ]
        if "Hyponatremia" in name:
            rec_parts += [
                "• Fluid restriction may be required — consult your nephrologist.",
                "• Identify the cause: excess fluid intake, diuretic use, or adrenal insufficiency.",
                "• Correct sodium gradually (too-rapid correction causes osmotic demyelination).",
            ]
        if "Hypokalemia" in name:
            rec_parts += [
                "• Identify cause: diuretic use, poor intake, GI losses.",
                "• Potassium supplementation may be required under medical supervision.",
            ]

    return Finding(
        condition="Electrolyte Imbalance",
        status=all_names,
        severity=combined_sev,
        icon="⚗️",
        color=_sev_color(combined_sev),
        parameters=params,
        explanation=combined_exp,
        triggered_by=all_triggers,
        recommendation="\n".join(dict.fromkeys(rec_parts)),  # deduplicate
    )


def detect_dehydration(sg: float) -> Finding:
    params = [
        {"name": "Specific Gravity", "value": sg, "unit": "(unitless)",
         "flag": _flag(sg, low=1.005, high=1.025)},
    ]

    if sg > 1.035:
        status = "Severe Dehydration / Concentrated Urine"
        severity = "critical"
        triggered = f"Specific Gravity {sg} — severely concentrated urine (> 1.035)"
        explanation = (
            "A specific gravity above 1.035 indicates extremely concentrated urine, suggesting "
            "severe dehydration or significantly reduced fluid intake. The kidneys are working hard "
            "to conserve water. In CKD patients, concentrated urine can accelerate kidney damage "
            "by increasing the concentration of toxic solutes."
        )
        rec = (
            "⚠️ Increase fluid intake immediately (unless medically restricted).\n"
            "• Target urine that appears pale yellow — dark yellow/amber is a sign of dehydration.\n"
            "• In CKD: consult your nephrologist for appropriate fluid targets.\n"
            "• Avoid diuretics without medical supervision.\n"
            "• Check for fever, excessive sweating, or vomiting as contributing factors."
        )
    elif sg > 1.030:
        status = "Possible Dehydration"
        severity = "warning"
        triggered = f"Specific Gravity {sg} — highly concentrated urine (> 1.030)"
        explanation = (
            "Specific gravity above 1.030 suggests the kidneys are concentrating urine excessively, "
            "which may indicate insufficient fluid intake (dehydration). "
            "Adequate hydration is critical for kidney health — water helps flush waste products "
            "through the nephrons and prevents crystal/stone formation."
        )
        rec = (
            "• Increase daily water intake — aim for pale-yellow urine colour.\n"
            "• Target 2–2.5 litres/day for CKD Low Risk; follow doctor's advice for higher risk.\n"
            "• Avoid excessive caffeine and alcohol which increase fluid losses.\n"
            "• If you are on fluid restriction, discuss optimal intake with your nephrologist."
        )
    elif sg < 1.005:
        status = "Over-hydration / Possible Kidney Concentration Defect"
        severity = "warning"
        triggered = f"Specific Gravity {sg} — very dilute urine (< 1.005)"
        explanation = (
            "Very low specific gravity may indicate over-hydration, or impaired kidney concentrating "
            "ability (a sign of advanced CKD or diabetes insipidus). "
            "Kidneys that cannot concentrate urine properly are losing their filtering efficiency."
        )
        rec = (
            "• Discuss this finding with your nephrologist — very dilute urine can signal CKD progression.\n"
            "• Assess for diabetes insipidus if occurring persistently.\n"
            "• Do not self-restrict fluids without medical guidance."
        )
    else:
        status = "Normal"
        severity = "normal"
        triggered = f"Specific Gravity {sg} is within normal range (1.005–1.030)"
        explanation = (
            "Urine specific gravity is within the normal range, indicating adequate hydration "
            "and normal kidney concentrating ability."
        )
        rec = (
            "• Maintain consistent daily fluid intake of 2–2.5 litres.\n"
            "• Adjust intake based on activity level, weather, and any medical restrictions."
        )

    return Finding(
        condition="Hydration Status",
        status=status,
        severity=severity,
        icon="💧",
        color=_sev_color(severity),
        parameters=params,
        explanation=explanation,
        triggered_by=triggered,
        recommendation=rec,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def run_health_screening(patient: dict) -> list:
    """
    Run all rule-based detectors on a patient data dict.
    Returns a list of Finding objects.
    """
    findings = [
        detect_diabetes(
            bg    = float(patient.get("BloodGlucose",   100)),
            sugar = int(patient.get("Sugar", 0)),
        ),
        detect_hypertension(
            bp    = float(patient.get("BloodPressure",  80)),
        ),
        detect_anemia(
            hgb   = float(patient.get("Hemoglobin",     13.0)),
            rbc   = float(patient.get("RBCCount",       4.5)),
            pcv   = float(patient.get("PackedCellVolume", 40)),
        ),
        detect_uti(
            wbc       = float(patient.get("WBCCount",   7800)),
            pus_cells = str(patient.get("PusCells",     "normal")),
            bacteria  = str(patient.get("Bacteria",     "notpresent")),
        ),
        detect_electrolyte_imbalance(
            sodium    = float(patient.get("Sodium",     138)),
            potassium = float(patient.get("Potassium",  4.5)),
        ),
        detect_dehydration(
            sg        = float(patient.get("SpecificGravity", 1.015)),
        ),
    ]
    return findings


def findings_summary(findings: list) -> dict:
    """Return counts by severity for a quick summary badge."""
    counts = {"critical": 0, "warning": 0, "normal": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    return counts
