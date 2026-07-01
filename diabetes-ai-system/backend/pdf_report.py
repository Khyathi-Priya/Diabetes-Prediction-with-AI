"""
Generates a downloadable PDF health report for a single prediction record.
Uses matplotlib to render the pie chart + radar chart as images, then lays
everything out with ReportLab.
"""
import io
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # headless, no display needed on the server
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

import ml_model

NEON_CYAN = colors.HexColor("#00E5FF")
DARK_NAVY = colors.HexColor("#0A1128")
RISK_COLORS = {"High": colors.HexColor("#FF3B5C"), "Moderate": colors.HexColor("#FFB020"), "Low": colors.HexColor("#1FD976")}


def _pie_chart_image(probability: float) -> io.BytesIO:
    fig, ax = plt.subplots(figsize=(3.2, 3.2), dpi=150)
    healthy = max(0.0, 1 - probability) * 100
    risk = probability * 100
    colors_ = ["#00E5FF", "#FF3B5C"]
    ax.pie(
        [healthy, risk],
        labels=[f"Healthy {healthy:.1f}%", f"Risk {risk:.1f}%"],
        colors=colors_,
        startangle=90,
        textprops={"fontsize": 9},
    )
    ax.set_title("Risk Probability", fontsize=11)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def _radar_chart_image(radar: dict) -> io.BytesIO:
    labels = list(radar.keys())
    values = list(radar.values())
    values += values[:1]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(3.6, 3.6), dpi=150, subplot_kw={"polar": True})
    ax.plot(angles, values, color="#00E5FF", linewidth=2)
    ax.fill(angles, values, color="#00E5FF", alpha=0.3)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_yticklabels([])
    ax.set_title("Health Radar", fontsize=11, pad=20)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_report_pdf(user, prediction_record) -> io.BytesIO:
    """
    user: models.User
    prediction_record: models.Prediction
    Returns an in-memory PDF (BytesIO) ready to stream back to the client.
    """
    features = {
        "pregnancies": prediction_record.pregnancies,
        "glucose": prediction_record.glucose,
        "bloodpressure": prediction_record.bloodpressure,
        "skinthickness": prediction_record.skinthickness,
        "insulin": prediction_record.insulin,
        "bmi": prediction_record.bmi,
        "dpf": prediction_record.dpf,
        "age": prediction_record.age,
    }
    radar = ml_model.radar_data(features)
    recommendations = ml_model.recommendations_for(prediction_record.risk_level, features)
    label = "Diabetic" if prediction_record.prediction == 1 else "Non-Diabetic"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=18 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], textColor=DARK_NAVY, fontSize=20, spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle", parent=styles["Normal"], textColor=colors.HexColor("#0091B5"),
        fontSize=11, alignment=TA_CENTER, spaceAfter=14,
    )
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=DARK_NAVY, spaceBefore=14, spaceAfter=6)
    body = styles["BodyText"]

    elements = []
    elements.append(Paragraph("Diabetes Prediction AI System", title_style))
    elements.append(Paragraph("Health Risk Analysis Report", subtitle_style))

    risk_color = RISK_COLORS.get(prediction_record.risk_level, colors.grey)

    info_table_data = [
        ["Patient", user.username, "Email", user.email],
        ["Report Date", prediction_record.created_at.strftime("%d %b %Y, %I:%M %p"), "Prediction ID", f"#{prediction_record.id}"],
    ]
    info_table = Table(info_table_data, colWidths=[80, 140, 80, 140])
    info_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK_NAVY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6E4EE")),
    ]))
    elements.append(info_table)

    elements.append(Paragraph("Prediction Result", h2))
    result_table = Table([
        ["Result", "Probability", "Risk Level"],
        [label, f"{prediction_record.probability * 100:.1f}%", prediction_record.risk_level],
    ], colWidths=[150, 150, 140])
    result_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("TEXTCOLOR", (2, 1), (2, 1), risk_color),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (2, 1), (2, 1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6E4EE")),
    ]))
    elements.append(result_table)

    elements.append(Paragraph("Input Values", h2))
    input_rows = [
        ["Pregnancies", str(prediction_record.pregnancies), "Glucose", f"{prediction_record.glucose} mg/dL"],
        ["Blood Pressure", f"{prediction_record.bloodpressure} mm Hg", "Skin Thickness", f"{prediction_record.skinthickness} mm"],
        ["Insulin", f"{prediction_record.insulin} mu U/ml", "BMI", f"{prediction_record.bmi}"],
        ["Diabetes Pedigree", f"{prediction_record.dpf}", "Age", f"{prediction_record.age} yrs"],
    ]
    input_table = Table(input_rows, colWidths=[110, 110, 110, 110])
    input_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D6E4EE")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(input_table)

    elements.append(Paragraph("Visual Analytics", h2))
    pie_img = Image(_pie_chart_image(prediction_record.probability), width=170, height=170)
    radar_img = Image(_radar_chart_image(radar), width=190, height=190)
    chart_table = Table([[pie_img, radar_img]], colWidths=[220, 240])
    elements.append(chart_table)

    elements.append(Paragraph("AI Recommendations", h2))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", body))

    elements.append(Spacer(1, 16))
    footer_style = ParagraphStyle("Footer", parent=styles["Normal"], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    elements.append(Paragraph(
        "This report is generated by an AI model for informational purposes only and is not a medical "
        "diagnosis. Please consult a licensed healthcare professional.",
        footer_style,
    ))
    elements.append(Paragraph(
        f"Generated on {datetime.utcnow().strftime('%d %b %Y, %I:%M %p')} UTC",
        footer_style,
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
