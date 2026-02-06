"""
表情包数据模型和存储
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os


class MemeRecord(BaseModel):
    """表情包记录"""
    id: str
    prompt: str
    optimizedPrompt: str
    style: str
    imageUrl: str
    createdAt: str
    provider: str = "unknown"
    isMock: bool = False
    styleStrength: int = 2


class MemeStorage:
    """表情包存储（使用JSON文件）"""

    def __init__(self, storage_path: str = "meme_history.json"):
        self.storage_path = storage_path
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def save(self, record: MemeRecord) -> None:
        """保存记录"""
        records = self.get_all()
        records.insert(0, record)
        # 只保留最近100条
        records = records[:100]
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([r.dict() for r in records], f, ensure_ascii=False, indent=2)

    def get_all(self) -> List[MemeRecord]:
        """获取所有记录"""
        if not os.path.exists(self.storage_path):
            return []
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return [MemeRecord(**item) for item in data]
        except Exception:
            return []

    def delete(self, meme_id: str) -> bool:
        """删除记录"""
        records = self.get_all()
        original_count = len(records)
        records = [r for r in records if r.id != meme_id]
        if len(records) < original_count:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([r.dict() for r in records], f, ensure_ascii=False, indent=2)
            return True
        return False

    def get_by_id(self, meme_id: str) -> Optional[MemeRecord]:
        """根据ID获取记录"""
        records = self.get_all()
        for record in records:
            if record.id == meme_id:
                return record
        return None


# 全局存储实例
meme_storage = MemeStorage()
