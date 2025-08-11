from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.chat import router as chat_router

def create_app() -> FastAPI:
    app = FastAPI(title="carebridges-rag")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 필요 시 도메인으로 제한
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat_router)
    @app.get("/healthz")
    def healthz():
        return {"ok": True}
    return app

app = create_app()