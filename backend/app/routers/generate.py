from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, constr, conint
from typing import Optional
import uuid
import os
from datetime import datetime
import shutil

try:
    from app.services.prompt_optimizer import prompt_optimizer
    from app.services.image_generator import image_generator
    from app.services.image_processor import image_processor
    from app.services.caption_generator import caption_generator
    from app.services.template_library import template_library
    from app.services.image_upscaler import image_upscaler
    from app.models.meme import MemeRecord, meme_storage
except ImportError:
    from services.prompt_optimizer import prompt_optimizer
    from services.image_generator import image_generator
    from services.image_processor import image_processor
    from services.caption_generator import caption_generator
    from services.template_library import template_library
    from services.image_upscaler import image_upscaler
    from models.meme import MemeRecord, meme_storage

router = APIRouter()

image_upscaler.set_upload_dir(image_generator.upload_dir)


class GenerateRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1, max_length=200)
    style: str = "cartoon"
    styleStrength: conint(ge=1, le=3) = 2
    numVariants: conint(ge=1, le=6) = 1
    templateId: Optional[str] = None
    memeMode: bool = False
    addTextBubble: bool = True
    text: Optional[constr(max_length=60)] = None


class GeneratedImage(BaseModel):
    id: str
    imageUrl: str
    createdAt: str
    provider: Optional[str] = None
    isMock: Optional[bool] = None
    variantIndex: int = 0


class GenerateResponse(BaseModel):
    success: bool
    id: Optional[str] = None
    imageUrl: str
    optimizedPrompt: str
    createdAt: Optional[str] = None
    provider: Optional[str] = None
    isMock: Optional[bool] = None
    images: Optional[list[GeneratedImage]] = None
    error: Optional[str] = None


class OptimizePromptRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1, max_length=200)
    style: str = "cartoon"
    styleStrength: conint(ge=1, le=3) = 2
    memeMode: bool = False


@router.post("/generate")
async def generate_meme(request: GenerateRequest) -> GenerateResponse:
    try:
        # 1. 优化提示词
        optimized_prompt = await prompt_optimizer.optimize(
            request.prompt, request.style, request.styleStrength, request.memeMode
        )

        # 2. 生成图片（支持模板和多变体）
        num_variants = max(1, min(6, int(request.numVariants)))
        images: list[GeneratedImage] = []

        for idx in range(num_variants):
            if request.templateId:
                template = template_library.get_template(request.templateId)
                if not template:
                    raise Exception("Template not found")
                source_path = template["path"]
                filename = f"meme_{uuid.uuid4().hex[:8]}.png"
                target_path = os.path.join(
                    os.path.dirname(source_path).replace("templates", "uploads"),
                    filename,
                )
                shutil.copyfile(source_path, target_path)

                image_result = await image_generator.generate_from_template(
                    optimized_prompt, target_path, style=request.style
                )
            else:
                image_result = await image_generator.generate(
                    optimized_prompt, request.style
                )

            print(
                f"🧭 Variant {idx + 1}/{num_variants} provider: {image_result.provider}, mock: {image_result.is_mock}"
            )

            # 3. 图片后处理（添加文字气泡）
            if request.addTextBubble and request.text:
                image_result.path = image_processor.add_text_bubble(
                    image_result.path, request.text
                )

            # 4. 生成访问URL
            filename = os.path.basename(image_result.path)
            image_url = f"/static/uploads/{filename}"

            # 5. 保存记录
            created_at = datetime.utcnow().isoformat()
            record = MemeRecord(
                id=str(uuid.uuid4()),
                prompt=request.prompt,
                optimizedPrompt=optimized_prompt,
                style=request.style,
                imageUrl=image_url,
                createdAt=created_at,
                provider=image_result.provider,
                isMock=image_result.is_mock,
                styleStrength=request.styleStrength,
            )
            meme_storage.save(record)

            images.append(
                GeneratedImage(
                    id=record.id,
                    imageUrl=image_url,
                    createdAt=created_at,
                    provider=image_result.provider,
                    isMock=image_result.is_mock,
                    variantIndex=idx,
                )
            )

        primary = images[0]
        return GenerateResponse(
            success=True,
            id=primary.id,
            imageUrl=primary.imageUrl,
            optimizedPrompt=optimized_prompt,
            createdAt=primary.createdAt,
            provider=primary.provider,
            isMock=primary.isMock,
            images=images,
        )

    except Exception as e:
        return GenerateResponse(
            success=False,
            id=None,
            imageUrl="",
            optimizedPrompt="",
            createdAt=None,
            provider=None,
            isMock=None,
            error=str(e),
        )


@router.post("/optimize-prompt")
async def optimize_prompt(request: OptimizePromptRequest) -> dict:
    try:
        optimized = await prompt_optimizer.optimize(
            request.prompt, request.style, request.styleStrength, request.memeMode
        )
        return {"optimizedPrompt": optimized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def get_providers() -> dict:
    return {
        "providers": image_generator.get_provider_status(),
    }


@router.get("/templates")
async def get_templates() -> dict:
    return {"templates": template_library.list_templates()}


class CaptionRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1, max_length=200)
    style: str = "cartoon"
    memeMode: bool = False


@router.post("/caption")
async def generate_caption(request: CaptionRequest) -> dict:
    caption = caption_generator.generate(
        prompt=request.prompt,
        style=request.style,
        meme_mode=request.memeMode,
    )
    return {"caption": caption}


class CaptionBatchRequest(BaseModel):
    prompt: constr(strip_whitespace=True, min_length=1, max_length=200)
    style: str = "cartoon"
    memeMode: bool = False
    count: conint(ge=1, le=6) = 3


@router.post("/caption/batch")
async def generate_caption_batch(request: CaptionBatchRequest) -> dict:
    captions = caption_generator.generate_batch(
        prompt=request.prompt,
        style=request.style,
        meme_mode=request.memeMode,
        count=request.count,
    )
    return {"captions": captions}


class TemplateSyncRequest(BaseModel):
    source: str = Field(default="imgflip", description="imgflip | urls")
    limit: conint(ge=1, le=60) = 20
    force: bool = False
    urls: Optional[list[str]] = None


@router.post("/templates/sync")
async def sync_templates(request: TemplateSyncRequest) -> dict:
    source = (request.source or "imgflip").strip().lower()
    try:
        if source == "imgflip":
            result = template_library.sync_imgflip(limit=int(request.limit), force=request.force)
        elif source == "urls":
            urls = request.urls or []
            if not urls:
                raise HTTPException(status_code=400, detail="urls is required when source=urls")
            result = template_library.sync_urls(urls=urls, force=request.force)
        else:
            raise HTTPException(status_code=400, detail="Unsupported source")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return {
        "success": True,
        "result": result,
        "templates": template_library.list_templates(),
    }


class UpscaleRequest(BaseModel):
    imageUrl: constr(strip_whitespace=True, min_length=1)


@router.post("/upscale")
async def upscale_image(request: UpscaleRequest) -> dict:
    if not image_upscaler.is_available():
        raise HTTPException(status_code=400, detail="CLIPDROP_API_KEY not configured")

    filename = os.path.basename(request.imageUrl)
    source_path = os.path.join(image_generator.upload_dir, filename)
    if not os.path.exists(source_path):
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        upscaled_path = await image_upscaler.upscale(source_path)
        upscaled_filename = os.path.basename(upscaled_path)
        return {"imageUrl": f"/static/uploads/{upscaled_filename}"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
