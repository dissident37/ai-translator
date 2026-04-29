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
- [backend/services/groq_service.py](backend/services/groq_service.py) — Groq-Client; ruft `llama-3.3-70b-versatile` mit temperature 0.3, max 2048 Tokens auf; enthält den Systemprompt

**Frontend** (`frontend/index.html`): Einzelne HTML-Datei (~1220 Zeilen), kein Build-Schritt. Eingebettetes CSS und JS mit:
- Automatische Übersetzung mit 900ms Debounce nach Eingabe (max. 5000 Zeichen)
- Einklappbare Seitenleiste mit drei Bereichen in `localStorage`: Historie (`ub_history`, max. 50), Favoriten (`ub_favorites`, max. 100), Wörterbuch (`ub_dictionary`, max. 200)
- Wörterbuch wird automatisch befüllt, wenn ein einzelnes deutsches Wort übersetzt wird
- Spracherkennung (Web Speech API) und Sprachausgabe (`speechSynthesis`)
- Race-Condition-Schutz über Request-Zähler (nur die neueste Antwort wird gerendert)

## API

```
POST /api/translate
{ "text": "string", "direction": "de-ru" | "ru-de" }
→ { "result": "<JSON-String>" }
```

Das `result`-Feld enthält einen JSON-String (kein Markdown), den der Frontend-JS parst. Das Groq-Modell gibt manchmal Markdown-Codeblöcke zurück — der Service bereinigt diese defensiv (siehe `groq_service.py` Zeilen 132–140).

## Prompt-Logik und Antwortstruktur

Der Systemprompt in [groq_service.py](backend/services/groq_service.py) klassifiziert die Eingabe und gibt immer ein JSON-Objekt mit folgenden Feldern zurück:

| Feld | Typ | Bedeutung |
|---|---|---|
| `type` | `"verb"` \| `"noun"` \| `"adjective"` \| `"other"` \| `"text"` | Erkannter Eingabetyp |
| `source` | string \| null | Normalisierte Quellform (z.B. Infinitiv, Artikel+Nomen) |
| `translation` | string | Übersetzung |
| `translation_note` | string \| null | Kurze russische Erläuterung zur Übersetzung |
| `examples` | Array von `{de, ru}` | Verwendungsbeispiele (3 Stück bei Einzelwörtern) |
| `forms` | object \| null | Konjugation (Verben: Infinitiv, Präsens, Präteritum, Perfekt, Futur I, Imperativ) |
| `synonyms` | string[] | Synonyme |
| `linguistic_note` | string \| null | Russische Anmerkung zu Register/Grammatik/Idiomatik |
| `gender` | string \| null | Genus (nur Nomen: `der`/`die`/`das`) |
| `plural` | string \| null | Pluralform (nur Nomen) |

**Eingabetyp-Verhalten:**
- **Einzelnes deutsches Verb**: volle Konjugationstabelle (`forms`), 3 Beispiele, Synonyme, linguistische Notiz
- **Einzelnes deutsches Nomen**: Genus, Plural, 3 Beispiele, Synonyme
- **Mehrwörtiger deutscher Text**: nur `translation` + optionale `linguistic_note`, alle anderen Felder null/leer
- **Russische Eingabe (beliebige Länge)**: vereinfachter Modus — nur `type: "text"` und `translation`, keine Analyse

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
