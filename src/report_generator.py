"""
PDF report generation using ReportLab.
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os

from src.analysis import get_summary_stats, zone_summary, species_summary


def generate_pdf_report(df, output_path="outputs/reports/ecotree_report.pdf",
                        plot_paths=None):
    """Generate a professional multi-page PDF report."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.8*cm,
        leftMargin=1.8*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="MainTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a5f2a"),
        spaceAfter=6,
        alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name="SubTitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#555555"),
        alignment=TA_CENTER,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1a5f2a"),
        spaceBefore=16,
        spaceAfter=8
    ))

    story = []

    # ===== Cover / Header =====
    story.append(Paragraph("🌳 EcoTree Environmental Report", styles["MainTitle"]))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d %B %Y, %H:%M')}",
        styles["SubTitle"]
    ))
    story.append(Spacer(1, 8))

    # ===== Summary Metrics =====
    story.append(Paragraph("1. City-wide Summary", styles["Section"]))
    summary = get_summary_stats(df)

    data = [
        ["Metric", "Value"],
        ["Total Trees Monitored", f"{summary['total_trees']:,}"],
        ["Total Carbon Sequestered", f"{summary['total_carbon_tonnes']} tonnes / year"],
        ["Total Oxygen Produced", f"{summary['total_oxygen_tonnes']} tonnes / year"],
        ["Estimated Cooling Benefit", f"{summary['total_cooling_mwh']} MWh / year"],
        ["Average Health Score", f"{summary['avg_health']} / 100"],
        ["Healthy Trees", f"{summary['healthy_pct']}%"],
        ["Moderate Trees", f"{summary['moderate_pct']}%"],
        ["At Risk Trees", f"{summary['at_risk_pct']}%"],
        ["Critical Trees (Immediate Attention)", f"{summary['critical_count']}"],
        ["Average Tree Age", f"{summary['avg_age']} years"],
        ["Average DBH", f"{summary['avg_dbh']} cm"],
    ]

    table = Table(data, colWidths=[10*cm, 6.5*cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a5f2a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f4f9f4")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f4f9f4"), colors.HexColor("#e8f5e9")]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#a5d6a7")),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica"),
        ("FONTNAME", (1, 1), (1, -1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(table)

    # ===== Zone Summary =====
    story.append(Paragraph("2. Zone-wise Performance", styles["Section"]))
    zone_df = zone_summary(df).reset_index()
    zone_data = [["Zone", "Trees", "Carbon (kg)", "Avg Health", "Critical", "Avg Age"]]
    for _, row in zone_df.iterrows():
        zone_data.append([
            row["zone"],
            int(row["tree_count"]),
            f"{row['total_carbon_kg']:,.0f}",
            f"{row['avg_health']}",
            int(row["critical_trees"]),
            f"{row['avg_age']}"
        ])

    ztable = Table(zone_data, colWidths=[3.2*cm, 2*cm, 3.2*cm, 2.5*cm, 2.2*cm, 2.2*cm])
    ztable.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2e7d32")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#e8f5e9")]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(ztable)

    # ===== Species Summary =====
    story.append(Paragraph("3. Species Distribution & Impact", styles["Section"]))
    sp_df = species_summary(df).reset_index().head(10)
    sp_data = [["Species", "Count", "Avg Health", "Total Carbon (kg)", "Avg Age"]]
    for _, row in sp_df.iterrows():
        sp_data.append([
            row["species"],
            int(row["count"]),
            f"{row['avg_health']}",
            f"{row['total_carbon']:,.0f}",
            f"{row['avg_age']}"
        ])

    sptable = Table(sp_data, colWidths=[3.5*cm, 2*cm, 2.5*cm, 3.8*cm, 2.2*cm])
    sptable.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1565c0")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#e3f2fd")]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(sptable)

    # ===== Recommendations =====
    story.append(Paragraph("4. Key Recommendations", styles["Section"]))
    recommendations = """
    <b>Immediate Actions:</b><br/>
    • Schedule detailed field inspection for all <b>Critical</b> and <b>At Risk</b> trees within 30 days.<br/>
    • Prioritize watering, mulching and pest treatment for trees with health score below 50.<br/><br/>
    <b>Medium-term Strategy:</b><br/>
    • Increase planting density in zones showing lower carbon contribution.<br/>
    • Prefer high-sequestration species (Banyan, Peepal, Teak, Neem) for new plantations.<br/>
    • Establish a regular 6-month health monitoring cycle for trees older than 30 years.<br/><br/>
    <b>Long-term Vision:</b><br/>
    • Aim for &gt;75% trees in Healthy category within 3 years.<br/>
    • Develop a public-facing dashboard for citizen engagement and tree adoption programs.
    """
    story.append(Paragraph(recommendations, styles["Normal"]))

    # Footer note
    story.append(Spacer(1, 25))
    story.append(Paragraph(
        "<i>This report was auto-generated by the EcoTree system. "
        "Calculations are based on simplified allometric models and should be "
        "calibrated with local field data for operational use.</i>",
        styles["Normal"]
    ))

    doc.build(story)
    print(f"✅ PDF report saved → {output_path}")
    return output_path
