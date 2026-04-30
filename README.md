# Uebersetzer

AI translator and German learning assistant for DE <-> RU translation.

The project is intentionally focused on German: the main use case is translating German words, phrases, and texts into Russian with linguistic details that are useful while learning the language. Russian -> German translation is also supported, but the richer analysis pipeline is built around German input.

## Current Focus

Work is ongoing on the prompt system to improve two things at the same time:

- translation accuracy, especially for German grammar, register, idioms, articles, plural forms, and verb forms;
- token efficiency, by routing different input types to smaller specialized prompts instead of using one large universal prompt.

Prompt behavior is documented in [backend/prompts/WORKFLOW.md](backend/prompts/WORKFLOW.md). The application loads prompt text from that file at server startup.

## Features

- German -> Russian and Russian -> German translation.
- Structured JSON responses for the frontend.
- German single-word analysis with part of speech, article, plural, verb forms, examples, synonyms, and usage notes.
- Separate prompt paths for German words, short German text, long German text, and Russian -> German text.
- Automatic translation in the browser with debounce.
- Local browser history, favorites, and dictionary via `localStorage`.
- Automatic dictionary entries for single German word translations.
- Speech recognition and text-to-speech where supported by the browser.
- Backend serves both the API and the static frontend.

## Architecture

```text
frontend/index.html
  Single-file UI with embedded CSS and JavaScript.

backend/main.py
  FastAPI entry point, CORS, API router, static frontend hosting.

backend/routers/translate.py
  POST /api/translate validation and response model.

backend/services/groq_service.py
  Input classification, prompt selection, Groq call, token usage logging.

backend/services/llm_provider.py
  Provider abstraction and current Groq implementation.

backend/prompts/WORKFLOW.md
  Prompt workflow and prompt source sections.
```

The current LLM provider is Groq with `llama-3.3-70b-versatile`. Provider usage is isolated behind `LLMProvider`, so a different provider can be wired in with a small change in `backend/services/groq_service.py`.

## Prompt Routing

Input is classified before the model call:

| Key | Condition | Purpose |
| --- | --- | --- |
| `de_word` | `direction == "de-ru"` and 1 whitespace token | German word analysis and translation |
| `de_short` | `direction == "de-ru"` and 2-30 words | German phrase or short text translation with optional linguistic note |
| `de_long` | `direction == "de-ru"` and more than 30 words | Longer German text translation |
| `ru_de` | `direction == "ru-de"` | Russian -> German translation |

Each request logs token usage in the backend logs:

```text
token_usage kind=de_word prompt=90 completion=320 total=410
```

## API

```http
POST /api/translate
Content-Type: application/json

{
  "text": "entscheiden",
  "direction": "de-ru"
}
```

Response:

```json
{
  "result": {
    "type": "verb",
    "source": "sich entscheiden",
    "translation": "решаться, принимать решение",
    "translation_note": "...",
    "examples": [{ "de": "...", "ru": "..." }],
    "forms": { "Infinitiv": "..." },
    "synonyms": ["..."],
    "linguistic_note": "...",
    "gender": null,
    "plural": null
  }
}
```

`direction` must be either `de-ru` or `ru-de`. Empty text and invalid directions return HTTP 400.

## Setup

Requirements:

- Python 3.11+
- Groq API key

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create `.env`:

```bash
cp .env.example .env
```

Set:

```env
GROQ_API_KEY=your_api_key_here
```

Run locally:

```bash
cd backend
python main.py
```

Open:

```text
http://localhost:8000
```

There is currently no test or lint setup.

## Docker

```bash
docker compose up -d --build
```

The container exposes the app on host port `8001` and serves the FastAPI app on container port `8000`.

## Deployment

The production deployment is configured for an IONOS VPS behind Nginx. GitHub Actions deploys on every push to `main` by connecting over SSH, running `git pull`, and rebuilding the Docker container in `/srv/translate`.
