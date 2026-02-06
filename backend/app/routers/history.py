from fastapi import APIRouter
from typing import List

try:
    from app.models.meme import MemeRecord, meme_storage
except ImportError:
    from models.meme import MemeRecord, meme_storage

router = APIRouter()


@router.get("/history")
async def get_history() -> List[dict]:
    records = meme_storage.get_all()
    return [record.dict() for record in records]


@router.delete("/history/{meme_id}")
async def delete_history(meme_id: str):
    success = meme_storage.delete(meme_id)
    if not success:
        return {"success": False, "message": "记录不存在"}
    return {"success": True}
