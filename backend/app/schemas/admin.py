from pydantic import BaseModel


class GenerationStatsResponse(BaseModel):
    total_generations: int
    avg_processing_time: float
    by_status: dict[str, int]
