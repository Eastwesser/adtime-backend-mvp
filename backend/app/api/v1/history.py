from fastapi import APIRouter, Depends, Query
from app.core.dependencies import CurrentUserDep, get_db
from app.repositories.generation import GenerationRepository
from app.schemas.generation import GenerationResponse


router = APIRouter(
    prefix="",
    tags=["History"],
)


@router.get("/generations", response_model=list[GenerationResponse])
async def get_generation_history(
    user: CurrentUserDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db=Depends(get_db)
):
    """История генераций пользователя"""
    gen_repo = GenerationRepository(db)
    return await gen_repo.get_user_generations(
        user.id, 
        limit=per_page, 
        offset=(page-1)*per_page
    )
