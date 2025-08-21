from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.core.dependencies import CurrentUserDep, StorageDep
from app.services.storage import StorageService


router = APIRouter(
    prefix="",
    tags=["Upload"],
)


@router.post("/image")
async def upload_image(
    storage: StorageDep,
    user: CurrentUserDep,
    file: UploadFile = File(...),
):
    """Загрузить изображение для генерации"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Файл должен быть изображением")
    
    url = await storage.upload_image(file, user.id)
    return {"url": url, "filename": file.filename}
