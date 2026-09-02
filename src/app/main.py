from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as screening_router


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "web" / "static"


app = FastAPI(
    title="AI Resume Screening System",
    version="1.0.0",
)

app.include_router(screening_router)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")