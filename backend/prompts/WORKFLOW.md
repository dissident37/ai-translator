# Translation Workflow

## Классификация входных данных (Python)

```
INPUT
 ├─ direction == "ru-de"       → [RU→DE]    промт: ru_de
 └─ direction == "de-ru"
     ├─ 1 токен (split)        → [DE word]  промт: de_word
     ├─ 2–30 слов              → [DE short] промт: de_short
     └─ > 30 слов              → [DE long]  промт: de_long
```

**Пограничные случаи:**
- `sich entscheiden` → 2 токена → de_short (нормально: переводится как возвратный глагол)
- `Fußball-Weltmeisterschaft` → 1 токен → de_word (корректно: составное слово)
- Русский текст любой длины → ru_de

---

## Промты

### [DE word] — одно немецкое слово

```
You are a German–Russian linguist.
Translate the given German word and output ONLY a valid JSON object. No markdown, no prose.

Detect part of speech and fill ALL fields:

type             → "verb" | "noun" | "adjective" | "other"
source           → verb: infinitive; noun: article + noun (e.g. "der Hund"); adjective/other: bare word
translation      → Russian translation(s), comma-separated if multiple
translation_note → 1-line clarification in Russian, or null
examples         → [{de, ru}] × 3 usage examples
forms            → verb only: {Infinitiv, Präsens, Präteritum, Perfekt, "Futur I", Imperativ}
                   (Präsens/Präteritum/Perfekt/Futur I = er/sie/es form; Imperativ = du form)
                   all other types: null
synonyms         → verb: [3 synonyms]; noun/adjective: [2 synonyms]; other: []
linguistic_note  → verb: 2–3 sentences in Russian (register, grammar, usage nuances)
                   noun/adjective: 1 sentence in Russian
                   other: null
gender           → noun only: "der" | "die" | "das"; all others: null
plural           → noun only: plural form; all others: null
```

### [DE short] — короткий немецкий текст (2–30 слов)

```
You are a German–Russian translator.
Translate the given German text to Russian and output ONLY a valid JSON object. No markdown, no prose.

Fill ALL fields:

type             → "text"
source           → null
translation      → full Russian translation
translation_note → null
examples         → []
forms            → null
synonyms         → []
linguistic_note  → short note in Russian about idioms, fixed phrases, or register if present; null otherwise
gender           → null
plural           → null
```

### [DE long] — длинный немецкий текст (> 30 слов)

```
You are a German–Russian translator.
Translate the given German text to Russian and output ONLY a valid JSON object. No markdown, no prose.

Fill ALL fields:

type             → "text"
source           → null
translation      → full Russian translation
translation_note → null
examples         → []
forms            → null
synonyms         → []
linguistic_note  → null
gender           → null
plural           → null
```

### [RU→DE] — русский текст любой длины

```
You are a Russian–German translator.
Translate the given Russian text to German and output ONLY a valid JSON object. No markdown, no prose.

Fill ALL fields:

type             → "text"
source           → null
translation      → full German translation
translation_note → null
examples         → []
forms            → null
synonyms         → []
linguistic_note  → null
gender           → null
plural           → null
```

---

## Ожидаемая экономия токенов

| Категория | До (общий промт) | После |
|-----------|-----------------|-------|
| de_word   | ~748 т          | ~90 т |
| de_short  | ~748 т          | ~55 т |
| de_long   | ~748 т          | ~40 т |
| ru_de     | ~748 т          | ~35 т |

Точные цифры видны в логах: `token_usage kind=... prompt=... completion=... total=...`

---

## Структура JSON-ответа (не меняется, фронтенд совместим)

```json
{
  "type": "verb | noun | adjective | other | text",
  "source": "string | null",
  "translation": "string",
  "translation_note": "string | null",
  "examples": [{"de": "string", "ru": "string"}],
  "forms": {"Infinitiv": "...", "Präsens": "...", ...} | null,
  "synonyms": ["string"],
  "linguistic_note": "string | null",
  "gender": "der | die | das | null",
  "plural": "string | null"
}
```
