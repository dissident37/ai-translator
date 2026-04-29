from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any
from services.groq_service import translate_text

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str
    direction: str  # 'de-ru' oder 'ru-de'


class TranslateResponse(BaseModel):
    result: dict[str, Any]


@router.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """Nimmt Text und Richtung, gibt strukturiertes JSON zurück."""
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if request.direction not in ["de-ru", "ru-de"]:
        raise HTTPException(status_code=400, detail="Direction must be 'de-ru' or 'ru-de'")

    result = translate_text(request.text, request.direction)
    return TranslateResponse(result=result)
