import json
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv

from services.llm_provider import GroqProvider, TokenUsage

load_dotenv()

logger = logging.getLogger(__name__)

_provider = GroqProvider(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0.3,
    max_tokens=2048,
)

_WORKFLOW_PATH = Path(__file__).parent.parent / "prompts" / "WORKFLOW.md"

# Zuordnung: Klassifizierungsschlüssel → Überschrift in WORKFLOW.md
_SECTION_TITLES = {
    "de_word":  "[DE word]",
    "de_short": "[DE short]",
    "de_long":  "[DE long]",
    "ru_de":    "[RU→DE]",
}


def _load_prompts() -> dict[str, str]:
    """Liest Prompts aus WORKFLOW.md, extrahiert Codeblöcke aus den Abschnitten."""
    text = _WORKFLOW_PATH.read_text(encoding="utf-8")
    prompts: dict[str, str] = {}

    for key, title in _SECTION_TITLES.items():
        # Abschnitt zwischen ### <title> und dem nächsten ###
        section_pattern = rf"### {re.escape(title)}.*?\n(.*?)(?=\n### |\Z)"
        section_match = re.search(section_pattern, text, re.DOTALL)
        if not section_match:
            raise ValueError(f"Abschnitt '{title}' nicht in WORKFLOW.md gefunden")

        section_body = section_match.group(1)

        # Ersten ```...``` Block extrahieren
        code_match = re.search(r"```\n(.*?)```", section_body, re.DOTALL)
        if not code_match:
            raise ValueError(f"Kein Codeblock im Abschnitt '{title}' gefunden")

        prompts[key] = code_match.group(1).strip()

    return prompts


_PROMPTS: dict[str, str] = _load_prompts()


def _classify(text: str, direction: str) -> str:
    """Gibt den Prompt-Schlüssel zurück: ru_de | de_word | de_short | de_long."""
    if direction == "ru-de":
        return "ru_de"
    wc = len(text.split())
    if wc <= 5:
        return "de_word"
    return "de_short" if wc <= 30 else "de_long"


def _strip_markdown(raw: str) -> str:
    """Entfernt ```json ... ``` Wrapper falls das Modell ihn trotz Anweisung erzeugt."""
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return raw


def _log_usage(usage: TokenUsage, kind: str) -> None:
    logger.info(
        "token_usage kind=%s prompt=%d completion=%d total=%d",
        kind,
        usage.prompt_tokens,
        usage.completion_tokens,
        usage.total_tokens,
    )


def translate_text(text: str, direction: str) -> dict:
    """Übersetzt Text und gibt strukturiertes JSON zurück."""
    kind = _classify(text, direction)
    system = _PROMPTS[kind]
    raw, usage = _provider.complete(system, f"Translate:\n\n{text}")
    _log_usage(usage, kind)
    return json.loads(_strip_markdown(raw))
