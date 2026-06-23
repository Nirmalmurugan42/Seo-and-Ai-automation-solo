from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def write_pdf(rows, output_path):
    pdf = SimpleDocTemplate(str(output_path))
    styles = getSampleStyleSheet()
    content = []

    content.append(Paragraph("SEO Intelligence Report", styles["Title"]))
    content.append(Spacer(1, 12))

    for row in rows:
        rec = row.get("recommendation", {}) or {}

        content.append(Paragraph(f"Keyword: {row.get('keyword')}", styles["Heading2"]))
        content.append(Paragraph(f"Current Rank: {row.get('our_rank') or 'Not Ranked'}", styles["BodyText"]))
        content.append(Paragraph(f"Top Competitor: {row.get('top_company')}", styles["BodyText"]))
        content.append(Paragraph(f"Word Gap: {abs(row.get('word_gap', 0) or 0)}", styles["BodyText"]))
        content.append(Paragraph(f"Suggested Title: {rec.get('title_tag', '')}", styles["BodyText"]))
        content.append(Paragraph(f"Meta Description: {rec.get('meta_description', '')}", styles["BodyText"]))
        content.append(Paragraph(f"Content Brief: {rec.get('content_brief', '')}", styles["BodyText"]))
        content.append(Spacer(1, 12))

    pdf.build(content)
    return output_path