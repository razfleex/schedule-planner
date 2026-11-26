from fastapi import FastAPI

app = FastAPI(
    title="Schedule Planner",
    description="API для планирования учебных занятий и расписаний",
    version="0.1.0",
)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    """Проверяет доступность API."""
    return {"status": "ok"}
