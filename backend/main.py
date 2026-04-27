from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import translate
import uvicorn

app = FastAPI(title="Übersetzer API", version="1.0.0")

# CORS — Anfragen vom Frontend erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Übersetzungs-Router einbinden
app.include_router(translate.router, prefix="/api")

# Frontend als statische Dateien ausliefern
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)