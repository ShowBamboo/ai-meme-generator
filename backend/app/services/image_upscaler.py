"""
图片超清增强服务（Clipdrop）
"""

import os
import uuid
from typing import Optional
from io import BytesIO
import requests


class ClipdropUpscaler:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CLIPDROP_API_KEY")
        self.api_url = "https://clipdrop-api.co/image-upscaling/v1/upscale"
        self.upload_dir: Optional[str] = None

    def set_upload_dir(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def upscale(self, image_path: str) -> str:
        if not self.api_key:
            raise ValueError("CLIPDROP_API_KEY not set")
        if not self.upload_dir:
            raise ValueError("Upload dir not set")

        from PIL import Image

        image = Image.open(image_path)
        width, height = image.size
        target_width = min(width * 2, 2048)
        target_height = min(height * 2, 2048)

        headers = {"x-api-key": self.api_key, "accept": "image/png"}
        with open(image_path, "rb") as f:
            files = {"image_file": f}
            data = {"target_width": str(target_width), "target_height": str(target_height)}
            response = requests.post(
                self.api_url, headers=headers, files=files, data=data, timeout=180
            )

        if response.status_code >= 400:
            body_preview = response.text[:800].replace("\n", " ")
            raise Exception(f"Clipdrop upscale failed {response.status_code}: {body_preview}")

        content_type = response.headers.get("Content-Type", "")
        if "image" not in content_type:
            raise Exception(f"Non-image response: {content_type}")

        image = Image.open(BytesIO(response.content))
        filename = f"upscaled_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.upload_dir, filename)
        image.save(filepath, "PNG")
        return filepath


image_upscaler = ClipdropUpscaler()
