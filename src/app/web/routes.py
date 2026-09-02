from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter()


@router.get("/")
def home():
    return FileResponse(
        "src/app/web/static/index.html"
    )