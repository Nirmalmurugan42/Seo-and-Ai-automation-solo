# AI-Powered SEO Intelligence Agent — Jypra Group

An automation of the workflow in your project PDF. It tracks your live Google
rankings, analyses the competitors who outrank you, finds the content gaps, and
uses an LLM to generate optimized titles, meta descriptions, heading outlines,
FAQs and content briefs — then exports an Excel + HTML action plan.

---

## ⚠️ Read this first — what this tool can and cannot do

**It cannot, by itself, put the site on page 1 or 2.** No software can. Google
rankings are earned by publishing better content, fixing technical issues, and
earning links — then waiting weeks for re-crawling.

Your own data shows the real blockers:
- jypragroup.com.au — Authority Score **5**, **~0** organic traffic, mobile
  PageSpeed **36** (competitors: 65–74).
- That PageSpeed score is a ranking anchor. **Fix site speed first** — no amount
  of AI copy compensates for a slow, low-authority site.

**What this agent *does* deliver** (the achievable, valuable part):
1. Live rank tracking for your target keywords.
2. Competitor on-page analysis (title, meta, headings, word count, links).
3. Factual gap analysis (what they have that you don't).
4. AI-generated, ready-to-paste title/meta/H1/H2/FAQ + a content brief.
5. An Excel + HTML report your SEO team can action immediately.

The fastest wins are the **18 "Quick Win" keywords** in your focus list
(difficulty ≤ 35) where Tesserent/CyberCX rank but you don't yet. The agent
loads those first automatically.

---

## How your three tools + Semrush fit together

| Tool | Role in this build | Needed? |
|---|---|---|
| **SerpAPI** | Runs the live Google search → your current rank + competitor URLs | **Yes** (core) |
| **Replicate AI** | Hosts the LLM that writes the optimized content | Yes (or swap for Anthropic/OpenAI) |
| **n8n** | No-code version of the same flow — see `n8n_workflow.json` | Optional alternative to the Python version |
| **Semrush** | Keyword **volume + difficulty** — *your SEO team already exported this to the CSVs*, so the agent reads those. A paid Semrush API is **not required**. | Optional refresh only |

So: the CSVs cover the Semrush data; SerpAPI does live ranking; Replicate writes
the copy. You don't need to pay for the Semrush API to run this.

---

## Setup (Python version — recommended)

```bash
cd seo_agent
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env        # then edit .env and paste your keys
```

Edit `.env`:
- `SERPAPI_KEY` — free key at https://serpapi.com (100 searches/month free)
- `LLM_PROVIDER=replicate` + `REPLICATE_API_TOKEN`
  (or `anthropic` / `openai` if you prefer — change the one line)
- `MAX_KEYWORDS=10` — start small; each keyword = 1 SerpAPI credit + 1 LLM call

Run it:

```bash
python -m core.main
```

Output lands in `reports/`:
- `seo_report_<date>.xlsx` — one row per keyword for your SEO team
- `seo_report_<date>.html` — readable brief (open in Chrome → Print → Save as PDF for your lead)

### Try it with no keys first (offline smoke test)
```bash
OFFLINE_DEMO=1 python -m core.data_loader   # confirms it reads your CSVs
```

---

## Project layout

```
seo_agent/
├── core/
│   ├── config.py        # all settings + keys (from .env)
│   ├── data_loader.py   # reads your SEO team's CSV keyword lists
│   ├── serp_client.py   # SerpAPI: live rank + competitor discovery
│   ├── scraper.py       # extracts title/meta/headings/word count/links
│   ├── analyzer.py      # TF-IDF gap analysis (factual layer)
│   ├── llm_client.py    # Replicate/Anthropic/OpenAI content generation
│   ├── reporter.py      # writes Excel + HTML reports
│   └── main.py          # the agent — orchestrates the 12-step pipeline
├── data/                # your 3 CSVs live here
├── reports/             # generated output
├── n8n_workflow.json    # importable no-code version
├── requirements.txt
└── .env.example
```

---

## n8n version

In n8n: **Workflows → Import from File → `n8n_workflow.json`**.
Set `SERPAPI_KEY` and `ANTHROPIC_API_KEY` in n8n's environment variables.
The workflow does one keyword end-to-end (Trigger → SerpAPI → parse → fetch
competitor → extract → LLM → parse). To run all keywords, add a **Google
Sheets / Read CSV** node before "Set Keyword" and loop; add a **Google Sheets
Append** node at the end to log results.

---

## The honest roadmap to page 1/2 (what to tell your lead)

1. **Week 0 — technical fixes** (biggest lever): get mobile PageSpeed from 36 to
   70+ (image compression, caching, lazy-load, remove render-blocking JS).
2. **Weeks 1–4 — Quick Wins**: run this agent on the 18 low-difficulty keywords,
   publish the generated content on the mapped target pages.
3. **Weeks 4–12 — authority**: earn backlinks (directory listings your
   competitors have: GoodFirms, Clutch, TechBehemoths, AFR mentions), publish the
   informational/blog content the agent briefs.
4. **Ongoing — monitor**: re-run weekly to track rank movement.

Realistic timeline to see Quick-Win keywords reach page 1/2: **2–4 months**,
assuming the technical and content work is actually published.
