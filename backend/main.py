from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, chat, emotions

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindEcho API",
    description="心灵回声 - 中国大学生心理健康平台",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(emotions.router)


@app.get("/")
def root():
    return {"message": "欢迎使用心灵回声 MindEcho API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "MindEcho"}
