""""
LLM layer — turns the factual GapReport into SEO recommendations.

Supported providers:
    replicate
    anthropic
    openai
    ollama
"""

from __future__ import annotations

import json
import requests

from . import config
from .analyzer import GapReport

SYSTEM = (
    "You are a senior SEO copywriter for an Australian cybersecurity "
    "consultancy. You write clear, credible, Australian-English copy that "
    "earns trust with SMB, government and enterprise buyers. You never invent "
    "certifications or false claims. You optimise for search intent, not "
    "keyword stuffing."
)


def _build_prompt(gap: GapReport, brand: str, target_page: str, intent: str) -> str:
    missing = ", ".join(gap.missing_terms) or "(none detected)"
    comp_titles = " | ".join(gap.competitor_titles[:3]) or "(none)"

    return f"""
Optimise our page for the keyword: "{gap.keyword}"
Search intent: {intent or "commercial/informational"}
Our target page: {target_page or "(home/service page)"}
Brand: {brand}

FACTS FROM ANALYSIS:
- Keyword currently in our title? {gap.keyword_in_title}
- Keyword currently in our H1? {gap.keyword_in_h1}
- Our word count: {gap.our_word_count}
- Competitor average word count: {gap.competitor_avg_word_count}
- Our H2 sections: {gap.our_h2_count}
- Competitor average H2 count: {gap.competitor_avg_h2_count}
- Keyword density: {gap.keyword_density_pct}%
- Missing competitor terms: {missing}
- Competitor page titles: {comp_titles}

Return ONLY valid JSON with this exact schema:
{{
  "title_tag": "string, <=60 chars, includes the keyword naturally",
  "meta_description": "string, <=155 chars, compelling, includes keyword",
  "h1": "string",
  "h2_outline": ["5-8 H2 section headings"],
  "faqs": [
    {{"q": "question", "a": "concise answer"}}
  ],
  "content_brief": "3-5 sentences telling the writer what to add/change",
  "priority_actions": ["3-5 short ordered TODO items"],
  "seo_topics": [
    {{
      "topic_name": "Topic name from missing competitor terms",
      "why_it_matters": "Explain why this topic matters for SEO",
      "recommended_content": "Write 100-150 words of useful recommended content",
      "suggested_h2": "SEO-friendly H2 heading",
      "recommended_word_count": "150-300 words",
      "ranking_benefit": "Explain how this topic helps improve Google rankings"
    }}
  ],
  "topic_content": [
    {{
      "topic": "SEO topic name",
      "why_it_matters": "Why this topic matters for SEO",
      "content": "Write 150-250 words of SEO-ready website content",
      "recommended_word_count": "150-250 words",
      "ranking_benefit": "How this helps improve Google rankings"
    }}
  ]
}}

Generate exactly 3 seo_topics.
Generate exactly 2 topic_content items.
Return valid JSON only.
Do not include markdown.
Do not include explanation.
Start with {{ and end with }}.
""".strip()


def _parse_json(raw: str) -> dict:
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()

    start = raw.find("{")
    end = raw.rfind("}")

    if start != -1 and end != -1:
        raw = raw[start:end + 1]

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "_raw": raw,
            "_error": "Model did not return valid JSON.",
        }


def _call_replicate(prompt: str) -> str:
    import replicate

    output = replicate.run(
        config.REPLICATE_MODEL,
        input={
            "system_prompt": SYSTEM,
            "prompt": prompt,
            "max_tokens": 1200,
            "temperature": 0.4,
        },
    )

    return "".join(output) if isinstance(output, (list, tuple)) else str(output)


def _call_anthropic(prompt: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    msg = client.messages.create(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1200,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    return msg.content[0].text


def _call_openai(prompt: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        temperature=0.4,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


def _call_ollama(prompt: str) -> str:
    model = getattr(config, "OLLAMA_MODEL", "llama3.2:3b")
    url = getattr(config, "OLLAMA_URL", "http://localhost:11434/api/generate")

    response = requests.post(
        url,
        json={
            "model": model,
            "prompt": (
                SYSTEM
                + "\n\nIMPORTANT INSTRUCTIONS:\n"
                + "- Return ONLY valid JSON.\n"
                + "- Do NOT use markdown.\n"
                + "- Do NOT use ```json fences.\n"
                + "- Do NOT explain anything.\n"
                + "- Start with { and end with }.\n\n"
                + prompt
            ),
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
                "num_predict": 1200,
            },
        },
        timeout=600,
    )

    response.raise_for_status()
    result = response.json()

    if isinstance(result, dict):
        return result.get("response", "")

    return str(result)


_PROVIDERS = {
    "replicate": _call_replicate,
    "anthropic": _call_anthropic,
    "openai": _call_openai,
    "ollama": _call_ollama,
}


def generate_recommendations(
    gap: GapReport,
    brand: str = config.OWN_BRAND,
    target_page: str = "",
    intent: str = "",
) -> dict:
    provider = config.LLM_PROVIDER.lower().strip()

    if provider not in _PROVIDERS:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Use one of: {list(_PROVIDERS)}"
        )

    prompt = _build_prompt(gap, brand, target_page, intent)
    raw = _PROVIDERS[provider](prompt)

    result = _parse_json(raw)
    result["_provider"] = provider

    return result