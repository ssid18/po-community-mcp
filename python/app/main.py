from fastapi import FastAPI
from app.routes.validate import router

app = FastAPI(
    title="Clinical Decision Guardrail MCP",
    description="Real-time safety gateway for clinical AI actions",
    version="1.0.0",
)

app.include_router(router)
