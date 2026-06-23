import subprocess
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

API_KEY = "jypra_seo_2026"

app = FastAPI(title="SEO Intelligence Agent API")

PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"

# Serve reports directory
app.mount("/reports", StaticFiles(directory=str(REPORTS_DIR)), name="reports")


@app.get("/")
def home():
    return {"status": "SEO Agent API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/latest-html")
def latest_html():
    files = sorted(REPORTS_DIR.glob("*.html"), reverse=True)

    if not files:
        raise HTTPException(status_code=404, detail="No HTML report found")

    latest_file = files[0]

    return FileResponse(
        latest_file,
        media_type="text/html",
        filename=latest_file.name,
    )


@app.get("/latest-pdf")
def latest_pdf():
    files = sorted(REPORTS_DIR.glob("*.pdf"), reverse=True)

    if not files:
        raise HTTPException(status_code=404, detail="No PDF report found")

    latest_file = files[0]

    return FileResponse(
        latest_file,
        media_type="application/pdf",
        filename=latest_file.name,
    )


@app.get("/latest-excel")
def latest_excel():
    files = sorted(REPORTS_DIR.glob("*.xlsx"), reverse=True)

    if not files:
        raise HTTPException(status_code=404, detail="No Excel report found")

    latest_file = files[0]

    return FileResponse(
        latest_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=latest_file.name,
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():

    html_files = sorted(REPORTS_DIR.glob("*.html"), reverse=True)
    pdf_files = sorted(REPORTS_DIR.glob("*.pdf"), reverse=True)
    xlsx_files = sorted(REPORTS_DIR.glob("*.xlsx"), reverse=True)

    latest_html_name = html_files[0].name if html_files else "Not Available"
    latest_pdf_name = pdf_files[0].name if pdf_files else "Not Available"
    latest_excel_name = xlsx_files[0].name if xlsx_files else "Not Available"

    return f"""
    <html>
    <head>
        <title>SEO Intelligence Dashboard</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f7fb;
                padding: 30px;
            }}

            h1 {{
                color: #2E5B8F;
            }}

            .card {{
                background: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 10px;
                border: 1px solid #e3e9f2;
                box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
            }}

            .btn {{
                display: inline-block;
                padding: 10px 18px;
                margin-top: 5px;
                margin-bottom: 10px;
                background: #2E5B8F;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}

            .btn:hover {{
                background: #1f4166;
            }}
        </style>
    </head>

    <body>

        <h1>SEO Intelligence Agent Dashboard</h1>

        <div class="card">
            <h2>System Status</h2>
            <p>✅ FastAPI Running</p>
            <p>✅ SEO Agent Available</p>
            <p>✅ Report Downloads Enabled</p>
        </div>

        <div class="card">
            <h2>Latest Reports</h2>

            <p><b>HTML Report:</b> {latest_html_name}</p>
            <a class="btn" href="/latest-html" target="_blank">
                Download HTML Report
            </a>

            <br>

            <p><b>PDF Report:</b> {latest_pdf_name}</p>
            <a class="btn" href="/latest-pdf" target="_blank">
                Download PDF Report
            </a>

            <br>

            <p><b>Excel Report:</b> {latest_excel_name}</p>
            <a class="btn" href="/latest-excel" target="_blank">
                Download Excel Report
            </a>

        </div>

        <div class="card">
            <h2>API Endpoints</h2>
            <p><b>GET</b> /health</p>
            <p><b>GET</b> /dashboard</p>
            <p><b>GET</b> /latest-html</p>
            <p><b>GET</b> /latest-pdf</p>
            <p><b>GET</b> /latest-excel</p>
            <p><b>POST</b> /run-seo-agent</p>
        </div>

    </body>
    </html>
    """


@app.post("/run-seo-agent")
def run_seo_agent(x_api_key: str = Header(None)):

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )

    result = subprocess.run(
        [
            str(PROJECT_DIR / ".venv" / "Scripts" / "python.exe"),
            "-m",
            "core.main",
        ],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=1800,
    )

    return {
        "status": "success" if result.returncode == 0 else "failed",
        "stdout": result.stdout,
        "stderr": result.stderr,
    }