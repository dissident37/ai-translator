# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Abhängigkeiten installieren
pip install -r backend/requirements.txt

# Umgebung konfigurieren
cp .env.example .env
# GROQ_API_KEY in .env eintragen

# Backend starten (serviert auch das Frontend)
cd backend
python main.py
# Erreichbar unter http://localhost:8000
```

Es gibt keine Tests und kein Linting-Setup.

## Architecture

**Backend** (`backend/`): FastAPI-App, die das Frontend als statische Dateien ausliefert.

- [backend/main.py](backend/main.py) — Einstiegspunkt: CORS (alle Origins), statische Dateien aus `../frontend`, uvicorn mit `reload=True`
- [backend/routers/translate.py](backend/routers/translate.py) — `POST /api/translate`; validiert `text` (nicht leer) und `direction` (`de-ru` | `ru-de`)
- [backend/services/groq_service.py](backend/services/groq_service.py) — Groq-Client; ruft `llama-3.3-70b-versatile` mit temperature 0.3, max 2048 Tokens auf

**Frontend** (`frontend/index.html`): Einzelne HTML-Datei, kein Build-Schritt. Enthält eingebettetes CSS und JS mit eigenem Markdown-Parser, Übersetzungshistorie (localStorage, max. 20 Einträge) und Ctrl+Enter-Shortcut.

## API

```
POST /api/translate
{ "text": "string", "direction": "de-ru" | "ru-de" }
→ { "result": "string (markdown)" }
```

## Prompt-Logik

Der Systemprompt in [groq_service.py](backend/services/groq_service.py) passt die Ausgabe nach Eingabetyp an:

- **Einzelnes Wort (DE→RU)**: Artikel + Plural, Übersetzung, 3 Beispiele, Synonyme; Konjugationstabelle bei Verben
- **Kurzer Text** (<5 Sätze und <400 Zeichen): Übersetzung + Erklärung idiomatischer Ausdrücke
- **Langer Text** (≥5 Sätze oder ≥400 Zeichen): Übersetzung + bis zu 3 wichtige Phrasen
- **RU→DE**: vereinfachter Modus ohne ausführliche Grammatikanalyse
- Linguistische Erläuterungen immer auf Russisch

## Environment

- `GROQ_API_KEY` — einzige erforderliche Umgebungsvariable (Groq-Konsole)
- Keine Datenbank, kein persistenter Zustand außer der Groq-API
