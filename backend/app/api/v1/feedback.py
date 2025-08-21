from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.core.dependencies import CurrentUserDep, get_db
from app.repositories.generation import GenerationRepository


router = APIRouter(
    prefix="",
    tags=["Feedback"],
)


@router.post("/generation/{generation_id}")
async def submit_generation_feedback(
    generation_id: UUID,
    is_liked: bool,
    user: CurrentUserDep,
    db=Depends(get_db)
):
    """Оставить feedback для генерации"""
    gen_repo = GenerationRepository(db)
    generation = await gen_repo.get(generation_id)
    
    if not generation or generation.user_id != user.id:
        raise HTTPException(404, "Генерация не найдена")
    
    await gen_repo.update(generation_id, {"is_liked": is_liked})
    return {"status": "feedback_recorded"}
