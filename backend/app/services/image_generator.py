# -*- coding: utf-8 -*-
"""
图片生成服务
支持多种图像生成 API，按优先级：

1. Clipdrop (免费额度，需要 API Key)
2. Local SD WebUI (免费，需要本地 A1111)
3. Replicate FLUX (推荐，有免费试用)
4. Hugging Face Router (需要 token)
5. Pollinations.ai (免费)
6. Mock 生成 (开发测试)
"""

import os
import uuid
import urllib.parse
import requests
import base64
from typing import Optional, Dict, List
from io import BytesIO
from datetime import datetime
from dataclasses import dataclass


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _strip_data_url_prefix(data: str) -> str:
    if data.startswith("data:image"):
        return data.split(",", 1)[1]
    return data


@dataclass
class ImageResult:
    path: str
    provider: str
    is_mock: bool = False


class ReplicateGenerator:
    """Replicate FLUX 图片生成器 - 有免费试用额度"""

    def __init__(self, api_token: Optional[str] = None):
        self.api_url = "https://api.replicate.com/v1"
        self.api_token = api_token or os.getenv("REPLICATE_API_TOKEN")
        self.version = "black-forest-labs/FLUX.1-schnell:91aed44c916a5e4701ed83c1d4b84d097a76c07e8f1c7e9c6f85c8b3c0a73f1c"  # FLUX.1-schnell
        self.upload_dir = None

        if self.api_token:
            print(f"🤖 ReplicateGenerator initialized (FLUX.1-schnell)")
        else:
            print(f"🤖 ReplicateGenerator initialized (No API token - will fail)")

    def set_upload_dir(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def generate(
        self,
        prompt: str,
        style: str = "cartoon",
        width: int = 512,
        height: int = 512,
    ) -> str:
        """使用 Replicate FLUX 生成图片"""
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not set")

        print(f"🤖 Generating image with Replicate FLUX...")
        print(f"   Prompt: {prompt[:60]}...")
        print(f"   Style: {style}")

        enhanced_prompt = self._build_enhanced_prompt(prompt, style)

        # Replicate API call
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Prefer": "wait",  # Wait for result
        }

        payload = {
            "version": self.version,
            "input": {
                "prompt": enhanced_prompt,
                "width": width,
                "height": height,
                "num_inference_steps": 4,  # FLUX Schnell is fast
                "guidance_scale": 7.5,
            }
        }

        try:
            # Create prediction
            response = requests.post(
                f"{self.api_url}/predictions",
                headers=headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()

            # Get image URL
            if result.get("status") == "succeeded":
                image_url = result["output"]
            elif result.get("status") == "failed":
                raise Exception(f"Replicate generation failed: {result.get('error')}")
            else:
                # Poll for result
                get_url = result.get("urls", {}).get("get")
                if get_url:
                    for _ in range(60):  # Poll for 60 seconds
                        response = requests.get(get_url, headers=headers, timeout=10)
                        result = response.json()
                        if result["status"] == "succeeded":
                            image_url = result["output"]
                            break
                        elif result["status"] == "failed":
                            raise Exception(f"Replicate generation failed")
                        import time
                        time.sleep(1)
                else:
                    raise Exception("No output URL in response")

            # Download image
            image_response = requests.get(image_url, timeout=60)
            image_response.raise_for_status()

            from PIL import Image
            image = Image.open(BytesIO(image_response.content))

            filename = f"meme_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self.upload_dir, filename)
            image.save(filepath, "PNG")

            print(f"✅ Image saved: {filename}")
            return filepath

        except Exception as e:
            print(f"❌ Replicate error: {e}")
            raise

    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        """构建增强的提示词"""
        meme_enhancements = [
            "meme format",
            "expressive face",
            "clear features",
        ]

        style_enhancements = {
            "cartoon": ["cartoon style", "bold outlines", "saturated colors"],
            "hand-drawn": ["hand-drawn style", "sketch", "illustration"],
            "anime": ["anime style", "manga", "cel shaded"],
            "realistic": ["photorealistic", "realistic", "photo"],
            "retro": ["retro style", "pixel art", "8-bit"],
            "minimalist": ["minimalist", "simple", "clean lines"],
        }

        enhancements = meme_enhancements + style_enhancements.get(style, [])
        enhanced = f"{prompt}, {', '.join(enhancements)}"

        return enhanced


class HuggingFaceGenerator:
    """Hugging Face Router 图片生成器"""

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        self.upload_dir = None

        if self.api_token:
            print(f"🔧 HuggingFaceGenerator initialized (using router endpoint)")
        else:
            print(f"🔧 HuggingFaceGenerator initialized (No API token)")

    def set_upload_dir(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def generate(
        self,
        prompt: str,
        style: str = "cartoon",
        width: int = 512,
        height: int = 512,
    ) -> str:
        """使用 Hugging Face Router 生成图片"""
        if not self.api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN not set")

        print(f"🔧 Generating image with Hugging Face Router...")
        print(f"   Prompt: {prompt[:60]}...")

        enhanced_prompt = self._build_enhanced_prompt(prompt, style)

        # 使用新的 router 端点
        model = "black-forest-labs/FLUX.1-schnell"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": enhanced_prompt,
            "parameters": {
                "width": width,
                "height": height,
                "num_inference_steps": 4,
            }
        }

        try:
            response = requests.post(
                f"https://router.huggingface.co/{model}",
                headers=headers,
                json=payload,
                timeout=180
            )
            response.raise_for_status()

            from PIL import Image
            image = Image.open(BytesIO(response.content))

            filename = f"meme_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self.upload_dir, filename)
            image.save(filepath, "PNG")

            print(f"✅ Image saved: {filename}")
            return filepath

        except Exception as e:
            print(f"❌ Hugging Face error: {e}")
            raise

    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        """构建增强的提示词"""
        style_enhancements = {
            "cartoon": "cartoon style, bold outlines",
            "hand-drawn": "hand-drawn illustration, sketch",
            "anime": "anime art, manga style",
            "realistic": "photorealistic, realistic",
            "retro": "pixel art, 8-bit style",
            "minimalist": "minimalist design, clean lines",
        }

        enhancement = style_enhancements.get(style, "")
        return f"{prompt}, {enhancement}"


class LocalWebUIGenerator:
    """本地 Stable Diffusion WebUI (AUTOMATIC1111) 生成器 - 免费"""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("SD_WEBUI_URL", "")).rstrip("/")
        self.upload_dir = None

        if self.base_url:
            print(f"🧪 LocalWebUIGenerator initialized ({self.base_url})")
        else:
            print("🧪 LocalWebUIGenerator initialized (No SD_WEBUI_URL)")

    def set_upload_dir(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def is_available(self) -> bool:
        return bool(self.base_url)

    async def generate(
        self,
        prompt: str,
        style: str = "cartoon",
        width: int = 512,
        height: int = 512,
    ) -> str:
        """调用本地 SD WebUI 生成图片"""
        if not self.base_url:
            raise ValueError("SD_WEBUI_URL not set")

        print("🧪 Generating image with Local SD WebUI...")
        print(f"   Prompt: {prompt[:60]}...")

        enhanced_prompt = self._build_enhanced_prompt(prompt, style)

        payload = {
            "prompt": enhanced_prompt,
            "negative_prompt": os.getenv("SD_WEBUI_NEGATIVE", ""),
            "width": width,
            "height": height,
            "steps": int(os.getenv("SD_WEBUI_STEPS", "20")),
            "cfg_scale": float(os.getenv("SD_WEBUI_CFG", "7")),
            "sampler_name": os.getenv("SD_WEBUI_SAMPLER", "Euler a"),
        }

        try:
            response = requests.post(
                f"{self.base_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=180,
            )
            response.raise_for_status()
            result = response.json()

            images = result.get("images") or []
            if not images:
                raise Exception("No images in SD WebUI response")

            image_data = base64.b64decode(_strip_data_url_prefix(images[0]))

            from PIL import Image
            image = Image.open(BytesIO(image_data))

            filename = f"meme_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self.upload_dir, filename)
            image.save(filepath, "PNG")

            print(f"✅ Image saved: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Local SD WebUI error: {e}")
            raise

    async def img2img(
        self,
        prompt: str,
        image_path: str,
        style: str = "cartoon",
        denoise_strength: Optional[float] = None,
    ) -> str:
        if not self.base_url:
            raise ValueError("SD_WEBUI_URL not set")

        print("🧪 Generating image with Local SD WebUI (img2img)...")
        enhanced_prompt = self._build_enhanced_prompt(prompt, style)

        from PIL import Image
        image = Image.open(image_path).convert("RGB")
        width, height = image.size

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        init_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        payload = {
            "prompt": enhanced_prompt,
            "negative_prompt": os.getenv("SD_WEBUI_NEGATIVE", ""),
            "width": width,
            "height": height,
            "steps": int(os.getenv("SD_WEBUI_STEPS", "20")),
            "cfg_scale": float(os.getenv("SD_WEBUI_CFG", "7")),
            "sampler_name": os.getenv("SD_WEBUI_SAMPLER", "Euler a"),
            "denoising_strength": denoise_strength
            if denoise_strength is not None
            else float(os.getenv("SD_WEBUI_DENOISE", "0.55")),
            "init_images": [init_image],
        }

        response = requests.post(
            f"{self.base_url}/sdapi/v1/img2img",
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        result = response.json()
        images = result.get("images") or []
        if not images:
            raise Exception("No images in img2img response")

        image_data = base64.b64decode(_strip_data_url_prefix(images[0]))
        output = Image.open(BytesIO(image_data))

        filename = f"meme_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.upload_dir, filename)
        output.save(filepath, "PNG")
        return filepath

    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        style_enhancements = {
            "cartoon": "cartoon style, bold outlines",
            "hand-drawn": "hand-drawn illustration, sketch",
            "anime": "anime art, manga style",
            "realistic": "photorealistic, realistic",
            "retro": "pixel art, 8-bit style",
            "minimalist": "minimalist design, clean lines",
        }

        enhancement = style_enhancements.get(style, "")
        return f"{prompt}, {enhancement}, meme format"


class ClipdropGenerator:
    """Clipdrop 文生图生成器 - 有免费额度"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("CLIPDROP_API_KEY")
        self.api_url = "https://clipdrop-api.co/text-to-image/v1"
        self.upload_dir = None

        if self.api_key:
            print("🟦 ClipdropGenerator initialized")
        else:
            print("🟦 ClipdropGenerator initialized (No API key)")

    def set_upload_dir(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def is_available(self) -> bool:
        return bool(self.api_key)

    async def generate(
        self,
        prompt: str,
        style: str = "cartoon",
        width: int = 512,
        height: int = 512,
    ) -> str:
        if not self.api_key:
            raise ValueError("CLIPDROP_API_KEY not set")

        print("🟦 Generating image with Clipdrop...")
        print(f"   Prompt: {prompt[:60]}...")

        enhanced_prompt = self._build_enhanced_prompt(prompt, style)

        headers = {"x-api-key": self.api_key, "accept": "image/png"}
        # Clipdrop expects multipart/form-data
        files = {"prompt": (None, enhanced_prompt)}

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                files=files,
                timeout=180,
            )
            if response.status_code >= 400:
                body_preview = response.text[:800].replace("\n", " ")
                print(
                    f"❌ Clipdrop HTTP {response.status_code} body: {body_preview}"
                )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                raise Exception(f"Non-image response: {content_type}")

            from PIL import Image
            image = Image.open(BytesIO(response.content))

            filename = f"meme_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self.upload_dir, filename)
            image.save(filepath, "PNG")

            print(f"✅ Image saved: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Clipdrop error: {e}")
            raise

    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        style_enhancements = {
            "cartoon": "cartoon style, bold outlines",
            "hand-drawn": "hand-drawn illustration, sketch",
            "anime": "anime art, manga style",
            "realistic": "photorealistic, realistic",
            "retro": "pixel art, 8-bit style",
            "minimalist": "minimalist design, clean lines",
        }

        enhancement = style_enhancements.get(style, "")
        return f"{prompt}, {enhancement}, meme format"


class PollinationsGenerator:
    """Pollinations.ai 图片生成器 - 完全免费（暂时不可用）"""

    def __init__(self):
        self.base_url = "https://image.pollinations.ai/prompt"
        self.upload_dir = None
        print(f"🌻 PollinationsGenerator initialized (FREE - currently returning 502)")

    def set_upload_dir(self, upload_dir: str):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    async def generate(
        self,
        prompt: str,
        style: str = "cartoon",
        width: int = 512,
        height: int = 512,
    ) -> str:
        """使用 Pollinations.ai 生成图片"""
        print(f"🌐 Generating image with Pollinations.ai...")

        enhanced_prompt = self._build_enhanced_prompt(prompt, style)
        encoded_prompt = urllib.parse.quote(enhanced_prompt)
        params = {
            "width": width,
            "height": height,
            "nologo": "true",
            "seed": uuid.uuid4().int & 0xFFFFFFFF,
        }

        url = f"{self.base_url}/{encoded_prompt}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"

        print(f"   URL: {url[:80]}...")

        try:
            response = requests.get(url, timeout=120)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "image" not in content_type:
                raise Exception(f"Non-image response: {content_type}")

            from PIL import Image
            image = Image.open(BytesIO(response.content))

            filename = f"meme_{uuid.uuid4().hex[:8]}.png"
            filepath = os.path.join(self.upload_dir, filename)
            image.save(filepath, "PNG")

            print(f"✅ Image saved: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ Pollinations error: {e}")
            raise

    def _build_enhanced_prompt(self, prompt: str, style: str) -> str:
        style_map = {
            "cartoon": "cartoon style, bold outlines",
            "hand-drawn": "hand-drawn style",
            "anime": "anime style",
            "realistic": "realistic style",
            "retro": "retro style",
            "minimalist": "minimalist",
        }
        enhancement = style_map.get(style, "")
        return f"{prompt}, {enhancement}, meme format"


class ImageGenerator:
    """主图片生成器 - 自动选择最佳可用方式"""

    def __init__(self):
        # 路径设置
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.project_root = os.path.dirname(self.backend_dir)
        self.static_dir = os.path.join(self.project_root, "static")
        self.upload_dir = os.path.join(self.static_dir, "uploads")
        os.makedirs(self.upload_dir, exist_ok=True)

        # 初始化各生成器
        self.clipdrop = ClipdropGenerator()
        self.clipdrop.set_upload_dir(self.upload_dir)

        self.webui = LocalWebUIGenerator()
        self.webui.set_upload_dir(self.upload_dir)

        self.replicate = ReplicateGenerator()
        self.replicate.set_upload_dir(self.upload_dir)

        self.huggingface = HuggingFaceGenerator()
        self.huggingface.set_upload_dir(self.upload_dir)

        self.pollinations = PollinationsGenerator()
        self.pollinations.set_upload_dir(self.upload_dir)

        # API Token 配置
        self.clipdrop_key = os.getenv("CLIPDROP_API_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        self.hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        self.pollinations_enabled = _env_flag("POLLINATIONS_ENABLED", True)

        self.forced_provider = os.getenv("IMAGE_GENERATION_PROVIDER") or os.getenv(
            "IMAGE_PROVIDER"
        )
        order_env = os.getenv("IMAGE_GENERATION_PROVIDER_ORDER") or os.getenv(
            "IMAGE_PROVIDER_ORDER"
        )
        self.provider_order = self._build_provider_order(order_env)

        print(f"\n🎨 ImageGenerator initialized")
        print(f"   Upload dir: {self.upload_dir}")
        print(f"\n📊 Provider Priority:")
        print(f"   1. 🟦 Clipdrop (free quota, requires API key)")
        if self.clipdrop.is_available():
            print(f"      ✅ API key configured")
        else:
            print(f"      ❌ No API key - Set CLIPDROP_API_KEY")

        print(f"   2. 🧪 Local SD WebUI (free, requires SD_WEBUI_URL)")
        if self.webui.is_available():
            print(f"      ✅ SD_WEBUI_URL configured")
        else:
            print(f"      ❌ No SD_WEBUI_URL")

        print(f"   3. 🤖 Replicate FLUX (best quality, requires token)")
        if self.replicate_token:
            print(f"      ✅ Token configured")
        else:
            print(f"      ❌ No token - Set REPLICATE_API_TOKEN")

        print(f"   4. 🔧 Hugging Face Router (good quality, requires token)")
        if self.hf_token:
            print(f"      ✅ Token configured")
        else:
            print(f"      ❌ No token - Set HUGGINGFACE_API_TOKEN")

        print(f"   5. 🌻 Pollinations.ai (free, no token)")
        if self.pollinations_enabled:
            print(f"      ✅ Enabled")
        else:
            print(f"      ❌ Disabled (POLLINATIONS_ENABLED=false)")
        print(f"   6. 🎭 Mock (development only)")
        if self.forced_provider:
            print(f"\n🎯 Forced provider: {self.forced_provider}")
        if self.provider_order:
            print(f"🔀 Provider order: {', '.join(self.provider_order)}")
        print("")

    def _build_provider_order(self, order_env: Optional[str]) -> List[str]:
        if order_env:
            items = [item.strip().lower() for item in order_env.split(",") if item.strip()]
            return items
        return ["clipdrop", "webui", "replicate", "huggingface", "pollinations", "mock"]

    def get_provider_status(self) -> List[Dict[str, str]]:
        status = []
        providers = self.provider_order or []
        if self.forced_provider:
            providers = [self.forced_provider.lower()]

        for name in providers:
            if name == "webui":
                status.append(
                    {
                        "name": "webui",
                        "enabled": "true" if self.webui.is_available() else "false",
                        "detail": "SD_WEBUI_URL configured" if self.webui.is_available() else "Missing SD_WEBUI_URL",
                    }
                )
            elif name == "clipdrop":
                status.append(
                    {
                        "name": "clipdrop",
                        "enabled": "true" if self.clipdrop.is_available() else "false",
                        "detail": "API key configured" if self.clipdrop.is_available() else "Missing CLIPDROP_API_KEY",
                    }
                )
            elif name == "replicate":
                status.append(
                    {
                        "name": "replicate",
                        "enabled": "true" if self.replicate_token else "false",
                        "detail": "Token configured" if self.replicate_token else "Missing REPLICATE_API_TOKEN",
                    }
                )
            elif name == "huggingface":
                status.append(
                    {
                        "name": "huggingface",
                        "enabled": "true" if self.hf_token else "false",
                        "detail": "Token configured" if self.hf_token else "Missing HUGGINGFACE_API_TOKEN",
                    }
                )
            elif name == "pollinations":
                status.append(
                    {
                        "name": "pollinations",
                        "enabled": "true" if self.pollinations_enabled else "false",
                        "detail": "Enabled" if self.pollinations_enabled else "Disabled by POLLINATIONS_ENABLED",
                    }
                )
            elif name == "mock":
                status.append(
                    {
                        "name": "mock",
                        "enabled": "true",
                        "detail": "Development fallback",
                    }
                )
            else:
                status.append(
                    {
                        "name": name,
                        "enabled": "false",
                        "detail": "Unknown provider",
                    }
                )

        return status

    async def generate(
        self,
        prompt: str,
        style: str = "cartoon",
        width: int = 512,
        height: int = 512,
    ) -> ImageResult:
        """
        生成图片 - 自动选择最佳可用方式

        Priority: Clipdrop → Local WebUI → Replicate → HuggingFace → Pollinations → Mock
        """
        errors = []

        providers = self.provider_order
        if self.forced_provider:
            providers = [self.forced_provider.lower()]

        for provider in providers:
            if provider == "clipdrop":
                if not self.clipdrop.is_available():
                    continue
                try:
                    path = await self.clipdrop.generate(prompt, style, width, height)
                    return ImageResult(path=path, provider="clipdrop")
                except Exception as e:
                    print(f"⚠️ Clipdrop failed: {e}")
                    errors.append(f"clipdrop: {e}")
            if provider == "webui":
                if not self.webui.is_available():
                    continue
                try:
                    path = await self.webui.generate(prompt, style, width, height)
                    return ImageResult(path=path, provider="webui")
                except Exception as e:
                    print(f"⚠️ Local WebUI failed: {e}")
                    errors.append(f"webui: {e}")
            elif provider == "replicate":
                if not self.replicate_token:
                    continue
                try:
                    path = await self.replicate.generate(prompt, style, width, height)
                    return ImageResult(path=path, provider="replicate")
                except Exception as e:
                    print(f"⚠️ Replicate failed: {e}")
                    errors.append(f"replicate: {e}")
            elif provider == "huggingface":
                if not self.hf_token:
                    continue
                try:
                    path = await self.huggingface.generate(prompt, style, width, height)
                    return ImageResult(path=path, provider="huggingface")
                except Exception as e:
                    print(f"⚠️ Hugging Face failed: {e}")
                    errors.append(f"huggingface: {e}")
            elif provider == "pollinations":
                if not self.pollinations_enabled:
                    continue
                try:
                    path = await self.pollinations.generate(prompt, style, width, height)
                    return ImageResult(path=path, provider="pollinations")
                except Exception as e:
                    print(f"⚠️ Pollinations failed: {e}")
                    errors.append(f"pollinations: {e}")
            elif provider == "mock":
                print("🎭 Using Mock provider")
                return await self._generate_mock(prompt, style)

        print("🎭 All providers failed, using Mock")
        return await self._generate_mock(prompt, style)

    async def _generate_mock(self, prompt: str, style: str) -> ImageResult:
        """Mock 生成（开发测试用）"""
        from PIL import Image, ImageDraw, ImageFont

        w, h = 512, 512
        image = Image.new("RGB", (w, h), color=0x1E293B)
        draw = ImageDraw.Draw(image)

        draw.ellipse([50, 50, 462, 462], fill=0x334155, outline=0x6366F1, width=4)

        text = prompt[:25] + "..." if len(prompt) > 25 else prompt
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (w - tw) // 2
        y = (h - th) // 2

        draw.text((x, y), text, fill=0xF8FAFC, font=font)
        draw.text(((w - 100) // 2, y + 40), f"Style: {style}", fill=0x94A3B8, font=font)
        draw.text(((w - 80) // 2, y + 80), "[MOCK]", fill=0xF43F5E, font=font)

        filename = f"meme_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(self.upload_dir, filename)
        image.save(filepath)

        print(f"✅ Mock image saved: {filename}")
        return ImageResult(path=filepath, provider="mock", is_mock=True)

    async def generate_from_template(
        self,
        optimized_prompt: str,
        template_path: str,
        style: str = "cartoon",
    ) -> ImageResult:
        """
        尝试用本地 WebUI img2img 将提示词应用到模板。
        若 WebUI 不可用则回退为原模板。
        """
        if self.webui.is_available():
            try:
                path = await self.webui.img2img(
                    optimized_prompt, template_path, style=style
                )
                return ImageResult(path=path, provider="webui_img2img")
            except Exception as e:
                print(f"⚠️ WebUI img2img failed: {e}")

        return ImageResult(path=template_path, provider="template", is_mock=False)


# 全局实例
image_generator = ImageGenerator()
