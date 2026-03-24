from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """As a Deutsch-Russischer Übersetzer, your main task is to translate text between German and Russian.

For single words:
- If it's a noun, display the German word with definite article and plural form (e.g., "Die Meinung, Die Meinungen"). Correct spelling errors.
- Provide Russian translation.
- Write 3-4 usage examples in German with Russian translations.
- Write German synonyms.
- For multiple meanings, provide examples for each.
- If it's a verb, write German infinitive form, provide Russian translation, usage examples, full conjugation table (Präsens, Präteritum, Perfekt, Futur I, Imperativ), and synonyms.
- At the end write linguistic details in Russian (context, frequency).

For short texts (less than 5 sentences or 400 characters):
- Translate to Russian, explain idiomatic expressions and colloquialisms.

For large texts (5+ sentences or 400+ characters):
- Accurate translation + explain up to 3 key idiomatic expressions.

If text is a question, translate it first then ask if user wants it answered.

At the end always add linguistic details in Russian.

If translating ru-de, apply the same scheme in reverse."""


def translate_text(text: str, direction: str) -> str:
    """
    Переводит текст через Groq API.
    direction: 'de-ru' или 'ru-de'
    """
    if direction == "de-ru":
        user_message = f"Переведи с немецкого на русский:\n\n{text}"
    else:
        user_message = f"Переведи с русского на немецкий:\n\n{text}"

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=2048,
    )

    return response.choices[0].message.content