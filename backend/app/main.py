from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys

# 确保路径正确
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")

sys.path.insert(0, BACKEND_DIR)

from app.routers import generate, history

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时加载模型
    from app.services.image_generator import image_generator
    from app.services.prompt_optimizer import prompt_optimizer
    
    # 预加载模型（可选，延迟到首次使用时）
    print("🚀 AI Meme Generator Backend Started")
    print(f"📁 Static files: {STATIC_DIR}")
    print(f"📁 Upload directory: {UPLOAD_DIR}")
    yield
    # 清理资源
    print("👋 Shutting down...")


app = FastAPI(
    title="AI Meme Generator API",
    description="智能表情包生成器后端服务",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务 - 使用绝对路径
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 路由
app.include_router(generate.router, prefix="/api", tags=["生成"])
app.include_router(history.router, prefix="/api", tags=["历史"])


@app.get("/")
async def root():
    return {"message": "AI Meme Generator API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
