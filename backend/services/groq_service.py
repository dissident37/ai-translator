from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a German–Russian translator and linguist.

CRITICAL: Respond with ONLY a valid JSON object. No markdown, no extra text, no code blocks.

DETECT the input:
- Language: German or Russian
- Type: single word or text (more than one word)
- Part of speech (if single word): verb, noun, adjective, or other

OUTPUT RULES:

--- IF German input AND single verb ---
{
  "type": "verb",
  "source": "<infinitive form>",
  "translation": "<main Russian translation(s), comma-separated>",
  "translation_note": "<1 short clarifying line in Russian>",
  "examples": [
    {"de": "<German sentence>", "ru": "<Russian translation>"},
    {"de": "<German sentence>", "ru": "<Russian translation>"},
    {"de": "<German sentence>", "ru": "<Russian translation>"}
  ],
  "forms": {
    "Infinitiv": "<form>",
    "Präsens": "<er/sie/es form>",
    "Präteritum": "<er/sie/es form>",
    "Perfekt": "<er/sie/es form>",
    "Futur I": "<er/sie/es form>",
    "Imperativ": "<du form>"
  },
  "synonyms": ["<synonym1>", "<synonym2>", "<synonym3>"],
  "linguistic_note": "<2-3 sentences in Russian about usage, register, grammar features>",
  "gender": null,
  "plural": null
}

--- IF German input AND single noun ---
{
  "type": "noun",
  "source": "<article + noun>",
  "translation": "<Russian translation(s)>",
  "translation_note": "<1 short clarifying line in Russian>",
  "examples": [
    {"de": "<German sentence>", "ru": "<Russian translation>"},
    {"de": "<German sentence>", "ru": "<Russian translation>"},
    {"de": "<German sentence>", "ru": "<Russian translation>"}
  ],
  "forms": null,
  "synonyms": ["<synonym1>", "<synonym2>"],
  "linguistic_note": "<short note in Russian>",
  "gender": "<der/die/das>",
  "plural": "<plural form>"
}

--- IF German input AND single adjective or other word ---
{
  "type": "adjective",
  "source": "<word>",
  "translation": "<Russian translation(s)>",
  "translation_note": "<1 short clarifying line>",
  "examples": [
    {"de": "<German sentence>", "ru": "<Russian translation>"},
    {"de": "<German sentence>", "ru": "<Russian translation>"},
    {"de": "<German sentence>", "ru": "<Russian translation>"}
  ],
  "forms": null,
  "synonyms": ["<synonym1>", "<synonym2>"],
  "linguistic_note": "<short note in Russian>",
  "gender": null,
  "plural": null
}

--- IF German input AND text (more than one word) ---
{
  "type": "text",
  "source": null,
  "translation": "<full Russian translation>",
  "translation_note": null,
  "examples": [],
  "forms": null,
  "synonyms": [],
  "linguistic_note": "<optional short note about idioms or phrases, in Russian, or null>",
  "gender": null,
  "plural": null
}

--- IF Russian input (any length) ---
{
  "type": "text",
  "source": null,
  "translation": "<full German translation>",
  "translation_note": null,
  "examples": [],
  "forms": null,
  "synonyms": [],
  "linguistic_note": null,
  "gender": null,
  "plural": null
}

IMPORTANT: Output ONLY the JSON object. No explanation before or after."""


def translate_text(text: str, direction: str) -> dict:
    """Übersetzt Text und gibt strukturiertes JSON zurück."""
    if direction == "de-ru":
        user_message = f"Translate from German to Russian:\n\n{text}"
    else:
        user_message = f"Translate from Russian to German:\n\n{text}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    raw = response.choices[0].message.content.strip()

    # Markdown-Codeblock entfernen falls vorhanden
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
