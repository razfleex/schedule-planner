from fastapi import FastAPI

from schedule_planner.routers.teachers import router as teachers_router

app = FastAPI(
    title="Schedule Planner",
    description="API для планирования учебных занятий и расписаний",
    version="0.1.0",
)

app.include_router(teachers_router)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Проверяет доступность API."""
    return {"status": "ok"}
