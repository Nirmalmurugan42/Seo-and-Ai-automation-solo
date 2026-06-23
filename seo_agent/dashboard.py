import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SEO Intelligence Dashboard",
    layout="wide"
)

st.title("SEO Intelligence Dashboard - Jypra Group")

REPORT_DIR = Path("reports")
DB_PATH = Path("seo_history.db")

html_files = sorted(REPORT_DIR.glob("*.html"), reverse=True)
xlsx_files = sorted(REPORT_DIR.glob("*.xlsx"), reverse=True)
pdf_files = sorted(REPORT_DIR.glob("*.pdf"), reverse=True)

st.header("Report Summary")

col1, col2, col3 = st.columns(3)
col1.metric("HTML Reports", len(html_files))
col2.metric("Excel Reports", len(xlsx_files))
col3.metric("PDF Reports", len(pdf_files))

st.header("Ranking History")

if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        "SELECT * FROM ranking_history ORDER BY checked_at DESC",
        conn
    )
    conn.close()

    total_records = len(df)
    total_keywords = df["keyword"].nunique() if not df.empty else 0
    not_ranked = len(df[df["rank"] == "Not ranked"]) if not df.empty else 0

    k1, k2, k3 = st.columns(3)
    k1.metric("Total Records", total_records)
    k2.metric("Unique Keywords", total_keywords)
    k3.metric("Not Ranked Records", not_ranked)

    st.dataframe(df, width="stretch")

    st.subheader("Keyword Frequency")
    if not df.empty:
        keyword_counts = df["keyword"].value_counts()
        st.bar_chart(keyword_counts)

else:
    st.warning("seo_history.db not found")

st.header("Latest Reports")

if html_files:
    latest_html = html_files[0]
    st.write(f"Latest HTML Report: {latest_html}")

    with open(latest_html, "rb") as file:
        st.download_button(
            "Download Latest HTML Report",
            file,
            file_name=latest_html.name,
            mime="text/html"
        )
else:
    st.warning("No HTML report found")

if xlsx_files:
    latest_xlsx = xlsx_files[0]
    with open(latest_xlsx, "rb") as file:
        st.download_button(
            "Download Latest Excel Report",
            file,
            file_name=latest_xlsx.name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if pdf_files:
    latest_pdf = pdf_files[0]
    with open(latest_pdf, "rb") as file:
        st.download_button(
            "Download Latest PDF Report",
            file,
            file_name=latest_pdf.name,
            mime="application/pdf"
        )