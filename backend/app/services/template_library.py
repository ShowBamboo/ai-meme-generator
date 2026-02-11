"""
模板库服务
- 本地内置模板
- 支持从 Imgflip 拉取热梗模板
- 支持传入任意图片 URL 下载为本地模板（仅本地演示用途）
"""

import hashlib
import json
import os
import re
from typing import List, Dict, Optional
from urllib.parse import urlparse

import requests


class TemplateLibrary:
    def __init__(self):
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(backend_dir)
        static_dir = os.path.join(project_root, "static")
        self.template_dir = os.path.join(static_dir, "templates")
        os.makedirs(self.template_dir, exist_ok=True)

        self.remote_index_path = os.path.join(self.template_dir, "remote_index.json")
        self.remote_index = self._load_remote_index()

        # 本地默认模板（已存在于 static/templates 下）
        self.templates: List[Dict[str, str]] = [
            {
                "id": "dog",
                "name": "狗头",
                "filename": "dog.png",
                "sourceUrl": "local",
                "license": "Demo Only",
            },
            {
                "id": "cat",
                "name": "猫猫",
                "filename": "cat.png",
                "sourceUrl": "local",
                "license": "Demo Only",
            },
            {
                "id": "panda",
                "name": "熊猫头",
                "filename": "panda.png",
                "sourceUrl": "local",
                "license": "Demo Only",
            },
            {
                "id": "shock",
                "name": "震惊",
                "filename": "shock.png",
                "sourceUrl": "local",
                "license": "Demo Only",
            },
            {
                "id": "ingenuity_15",
                "name": "NASA 梗图 15",
                "filename": "ingenuity_meme_15.jpg",
                "sourceUrl": "https://commons.wikimedia.org/wiki/File:Ingenuity_memes_15.jpg",
                "license": "Public Domain (US Government)",
            },
            {
                "id": "ingenuity_07",
                "name": "NASA 梗图 07",
                "filename": "ingenuity_meme_07.jpg",
                "sourceUrl": "https://commons.wikimedia.org/wiki/File:Ingenuity_memes_07.jpg",
                "license": "Public Domain (US Government)",
            },
        ]

    def _load_remote_index(self) -> List[Dict[str, str]]:
        if not os.path.exists(self.remote_index_path):
            return []
        try:
            with open(self.remote_index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            return []
        except Exception:
            return []

    def _save_remote_index(self):
        with open(self.remote_index_path, "w", encoding="utf-8") as f:
            json.dump(self.remote_index, f, ensure_ascii=False, indent=2)

    def _guess_ext(self, url: str, content_type: str = "") -> str:
        parsed = urlparse(url)
        path = parsed.path.lower()
        for ext in [".jpg", ".jpeg", ".png", ".webp"]:
            if path.endswith(ext):
                return ext
        if "png" in content_type:
            return ".png"
        if "webp" in content_type:
            return ".webp"
        return ".jpg"

    def _sanitize_name(self, value: str, fallback: str = "模板") -> str:
        value = (value or "").strip()
        if not value:
            return fallback
        value = re.sub(r"\s+", " ", value)
        return value[:48]

    def _download_image(self, url: str, target_path: str, timeout: int = 30) -> None:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        content_type = (response.headers.get("Content-Type") or "").lower()
        if content_type and "image" not in content_type:
            raise ValueError(f"URL is not an image: {content_type}")

        with open(target_path, "wb") as f:
            f.write(response.content)

    def _upsert_remote_template(
        self,
        template_id: str,
        name: str,
        filename: str,
        source_url: str,
    ) -> None:
        for idx, item in enumerate(self.remote_index):
            if item.get("id") == template_id:
                self.remote_index[idx] = {
                    "id": template_id,
                    "name": name,
                    "filename": filename,
                    "sourceUrl": source_url,
                    "license": "Demo Only",
                }
                self._save_remote_index()
                return

        self.remote_index.append(
            {
                "id": template_id,
                "name": name,
                "filename": filename,
                "sourceUrl": source_url,
                "license": "Demo Only",
            }
        )
        self._save_remote_index()

    def _download_remote_template(
        self,
        template_id: str,
        name: str,
        source_url: str,
        force: bool = False,
    ) -> str:
        existing = None
        for item in self.remote_index:
            if item.get("id") == template_id:
                existing = item
                break

        if existing and not force:
            path = os.path.join(self.template_dir, existing["filename"])
            if os.path.exists(path):
                return "skipped"

        head = requests.head(source_url, timeout=15, allow_redirects=True)
        content_type = (head.headers.get("Content-Type") or "").lower()
        ext = self._guess_ext(source_url, content_type)
        filename = f"remote_{template_id}{ext}"
        path = os.path.join(self.template_dir, filename)

        self._download_image(source_url, path)
        self._upsert_remote_template(template_id, name, filename, source_url)
        return "added"

    def list_templates(self) -> List[Dict[str, str]]:
        items = []

        for template in self.templates:
            path = os.path.join(self.template_dir, template["filename"])
            if not os.path.exists(path):
                continue
            items.append(
                {
                    "id": template["id"],
                    "name": template["name"],
                    "previewUrl": f"/static/templates/{template['filename']}",
                    "sourceUrl": template["sourceUrl"],
                    "license": template["license"],
                }
            )

        for template in self.remote_index:
            filename = template.get("filename")
            if not filename:
                continue
            path = os.path.join(self.template_dir, filename)
            if not os.path.exists(path):
                continue
            items.append(
                {
                    "id": template["id"],
                    "name": template["name"],
                    "previewUrl": f"/static/templates/{filename}",
                    "sourceUrl": template.get("sourceUrl", ""),
                    "license": template.get("license", "Demo Only"),
                }
            )

        return items

    def get_template(self, template_id: str) -> Optional[Dict[str, str]]:
        for template in self.templates:
            if template["id"] == template_id:
                path = os.path.join(self.template_dir, template["filename"])
                if not os.path.exists(path):
                    return None
                return {
                    "id": template["id"],
                    "name": template["name"],
                    "path": path,
                }

        for template in self.remote_index:
            if template.get("id") == template_id:
                filename = template.get("filename")
                if not filename:
                    return None
                path = os.path.join(self.template_dir, filename)
                if not os.path.exists(path):
                    return None
                return {
                    "id": template_id,
                    "name": template.get("name", template_id),
                    "path": path,
                }

        return None

    def sync_imgflip(self, limit: int = 20, force: bool = False) -> Dict[str, int]:
        limit = max(1, min(60, int(limit)))
        response = requests.get("https://api.imgflip.com/get_memes", timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            raise RuntimeError("Imgflip API returned unsuccessful response")

        memes = (data.get("data") or {}).get("memes") or []
        memes = memes[:limit]

        added = 0
        skipped = 0
        failed = 0

        for meme in memes:
            meme_id = str(meme.get("id") or "").strip()
            name = self._sanitize_name(meme.get("name") or f"imgflip-{meme_id}")
            url = (meme.get("url") or "").strip()
            if not meme_id or not url:
                failed += 1
                continue

            template_id = f"imgflip_{meme_id}"
            try:
                result = self._download_remote_template(
                    template_id=template_id,
                    name=name,
                    source_url=url,
                    force=force,
                )
                if result == "added":
                    added += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"⚠️ Sync imgflip template failed ({template_id}): {e}")
                failed += 1

        return {
            "source": "imgflip",
            "requested": limit,
            "added": added,
            "skipped": skipped,
            "failed": failed,
        }

    def sync_urls(self, urls: List[str], force: bool = False) -> Dict[str, int]:
        clean_urls = [url.strip() for url in urls if url and url.strip()]
        clean_urls = clean_urls[:60]

        added = 0
        skipped = 0
        failed = 0

        for url in clean_urls:
            digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:10]
            parsed = urlparse(url)
            raw_name = os.path.basename(parsed.path).rsplit(".", 1)[0]
            name = self._sanitize_name(raw_name, fallback=f"URL模板-{digest[:6]}")
            template_id = f"url_{digest}"

            try:
                result = self._download_remote_template(
                    template_id=template_id,
                    name=name,
                    source_url=url,
                    force=force,
                )
                if result == "added":
                    added += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"⚠️ Sync URL template failed ({url}): {e}")
                failed += 1

        return {
            "source": "urls",
            "requested": len(clean_urls),
            "added": added,
            "skipped": skipped,
            "failed": failed,
        }


template_library = TemplateLibrary()
