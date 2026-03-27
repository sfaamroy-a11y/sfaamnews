"""
ai_writer.py - SFAAM NEWS V2
Har region ke liye alag Groq + Gemini key
Ek fail ho toh dusri automatically use ho
"""
import os, re, logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Per-region keys
REGION_KEYS = {
    "world":    {"groq": os.getenv("GROQ_KEY_WORLD",""),    "gemini": os.getenv("GEMINI_KEY_WORLD","")},
    "usa":      {"groq": os.getenv("GROQ_KEY_USA",""),      "gemini": os.getenv("GEMINI_KEY_USA","")},
    "uk":       {"groq": os.getenv("GROQ_KEY_UK",""),       "gemini": os.getenv("GEMINI_KEY_UK","")},
    "pakistan": {"groq": os.getenv("GROQ_KEY_PAKISTAN",""), "gemini": os.getenv("GEMINI_KEY_PAKISTAN","")},
    "india":    {"groq": os.getenv("GROQ_KEY_INDIA",""),    "gemini": os.getenv("GEMINI_KEY_INDIA","")},
}

SYSTEM_PROMPT = """You are a world-class journalist for SFAAM NEWS — a global news website.
Write articles that are:
- ENGAGING: Powerful hook, story-driven, short paragraphs
- ACCURATE: Keep all original facts and quotes
- SEO OPTIMIZED: Natural keywords, H2/H3 headings
- LENGTH: 700-900 words
- FORMAT: Markdown only

Output format:
# Title Here

[Article body]

META: 155 character SEO description
KEYWORDS: kw1, kw2, kw3, kw4, kw5"""

PROMPT = """Rewrite this news article for SFAAM NEWS.
Engaging, story-driven, SEO-optimized. Keep ALL facts accurate.

Original:
\"\"\"
{text}
\"\"\""""


def rewrite_article(text, fallback_title="", region="world"):
    """Try Groq first, fallback to Gemini automatically."""
    keys = REGION_KEYS.get(region, REGION_KEYS["world"])

    # Try Groq first
    if keys["groq"]:
        result = _try_groq(text, keys["groq"])
        if result:
            logger.info(f"  ✅ [{region}] Groq used")
            return _parse(result, fallback_title)

    # Fallback to Gemini
    if keys["gemini"]:
        result = _try_gemini(text, keys["gemini"])
        if result:
            logger.info(f"  ✅ [{region}] Gemini fallback used")
            return _parse(result, fallback_title)

    # Last resort
    logger.error(f"  ❌ [{region}] Both keys failed!")
    return {
        "title":    fallback_title,
        "body":     f"## {fallback_title}\n\n{text[:400]}...",
        "meta_desc": fallback_title[:155],
        "keywords": "",
    }


def _try_groq(text, key):
    try:
        from groq import Groq
        client   = Groq(api_key=key)
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            max_tokens=1400,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": PROMPT.format(text=text[:5000])},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Groq failed: {e}")
        return None


def _try_gemini(text, key):
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model    = genai.GenerativeModel("gemini-pro")
        prompt   = f"{SYSTEM_PROMPT}\n\n{PROMPT.format(text=text[:5000])}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.warning(f"Gemini failed: {e}")
        return None


def _parse(content, fallback_title):
    lines      = content.strip().split("\n")
    title      = fallback_title
    meta_desc  = ""
    keywords   = ""
    body_lines = []

    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("META:"):
            meta_desc = line[5:].strip()
        elif line.startswith("KEYWORDS:"):
            keywords = line[9:].strip()
        else:
            body_lines.append(line)

    body = "\n".join(body_lines).strip()
    if not meta_desc:
        meta_desc = body.replace("#","")[:155].strip()

    return {"title": title, "body": body, "meta_desc": meta_desc, "keywords": keywords}


def make_slug(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:80]
