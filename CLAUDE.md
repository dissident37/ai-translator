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

- [backend/main.py](backend/main.py) — Einstiegspunkt: CORS (alle Origins), statische Dateien aus `../frontend`, uvicorn ohne reload
- [backend/routers/translate.py](backend/routers/translate.py) — `POST /api/translate`; validiert `text` (nicht leer) und `direction` (`de-ru` | `ru-de`), gibt HTTP 400 bei Fehler
- [backend/services/groq_service.py](backend/services/groq_service.py) — Klassifiziert die Eingabe, wählt den passenden Prompt, ruft den Provider auf, loggt Token-Verbrauch
- [backend/services/llm_provider.py](backend/services/llm_provider.py) — Abstrakte `LLMProvider`-Klasse + `GroqProvider`-Implementierung; um den Provider zu wechseln, nur `_provider` in `groq_service.py` tauschen
- [backend/prompts/WORKFLOW.md](backend/prompts/WORKFLOW.md) — **Einzige Quelle der Wahrheit für alle Prompts**; enthält das Entscheidungsbaum-Diagramm und die vollständigen Prompt-Texte in benannten Sektionen

**Frontend** (`frontend/index.html`): Einzelne HTML-Datei (~1220 Zeilen), kein Build-Schritt. Eingebettetes CSS und JS mit:
- Automatische Übersetzung mit 900ms Debounce nach Eingabe (max. 5000 Zeichen)
- Einklappbare Seitenleiste mit drei Bereichen in `localStorage`: Historie (`ub_history`, max. 50), Favoriten (`ub_favorites`, max. 100), Wörterbuch (`ub_dictionary`, max. 200)
- Wörterbuch wird automatisch befüllt, wenn ein einzelnes deutsches Wort übersetzt wird
- Spracherkennung (Web Speech API) und Sprachausgabe (`speechSynthesis`)
- Race-Condition-Schutz über Request-Zähler (nur die neueste Antwort wird gerendert)

## Prompt-System

Die Eingabe wird in Python klassifiziert (`_classify` in `groq_service.py`), dann wird einer von vier spezialisierten Prompts gewählt:

| Schlüssel  | Bedingung                    | Inhalt des Prompts                                |
|------------|------------------------------|---------------------------------------------------|
| `de_word`  | DE, 1 Token                  | POS-Erkennung, Konjugation, Beispiele, Synonyme   |
| `de_short` | DE, 2–30 Wörter              | Übersetzung + `linguistic_note` (Idiome/Register) |
| `de_long`  | DE, > 30 Wörter              | Nur Übersetzung                                   |
| `ru_de`    | `direction == "ru-de"`       | Nur Übersetzung ins Deutsche                      |

**Prompts bearbeiten:** Sektionen `### [DE word]`, `### [DE short]` usw. in [backend/prompts/WORKFLOW.md](backend/prompts/WORKFLOW.md) anpassen. Der Codeblock (` ``` `) in jeder Sektion wird beim Serverstart als Prompt geladen — kein Python-Code ändern nötig.

**Token-Logging:** Jede Anfrage schreibt eine Zeile ins uvicorn-Log:
```
token_usage kind=de_word prompt=90 completion=320 total=410
```

## API

```
POST /api/translate
{ "text": "string", "direction": "de-ru" | "ru-de" }
→ { "result": "<JSON-String>" }
```

Das `result`-Feld enthält einen JSON-String (kein Markdown), den der Frontend-JS parst. Das Modell gibt manchmal Markdown-Codeblöcke zurück — `_strip_markdown()` in `groq_service.py` bereinigt diese defensiv.

## JSON-Antwortstruktur (alle Felder immer vorhanden)

| Feld | Typ | Bedeutung |
|---|---|---|
| `type` | `"verb"` \| `"noun"` \| `"adjective"` \| `"other"` \| `"text"` | Erkannter Eingabetyp |
| `source` | string \| null | Normalisierte Quellform (Infinitiv, Artikel+Nomen, …) |
| `translation` | string | Übersetzung |
| `translation_note` | string \| null | Kurze russische Erläuterung |
| `examples` | `[{de, ru}]` | 3 Beispiele bei Einzelwörtern, sonst `[]` |
| `forms` | object \| null | Konjugation nur bei Verben |
| `synonyms` | string[] | Synonyme, sonst `[]` |
| `linguistic_note` | string \| null | Anmerkung zu Register/Idiomatik |
| `gender` | string \| null | `der`/`die`/`das`, nur bei Nomen |
| `plural` | string \| null | Pluralform, nur bei Nomen |

## Environment

- `GROQ_API_KEY` — einzige erforderliche Umgebungsvariable (Groq-Konsole)
- Keine Datenbank, kein persistenter Zustand außer dem Browser-`localStorage`

## Deployment

Die App läuft auf einem IONOS VPS (`translate.konstantinsittner.de`) hinter Nginx als Reverse Proxy auf Port 8001.

```bash
# Docker-Image bauen und Container starten
docker compose up -d --build

# Logs prüfen
docker logs uebersetzer_app
```

Autodeploy läuft über GitHub Actions (`.github/workflows/deploy.yml`): jeder Push auf `main` löst via SSH `git pull` + `docker compose up -d --build` auf dem Server aus. Server-Einstiegspunkt: `/srv/translate/`.

Das Frontend wird vom Backend aus `../frontend` (relativ zu `backend/`) ausgeliefert — funktioniert lokal und im Docker-Container (`WORKDIR /app/backend`).
