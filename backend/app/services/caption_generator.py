"""
自动文案生成器
根据输入和风格给出更有梗的短句
可选接入外部模型（OpenAI-compatible Chat Completions）
"""

import os
import random
import requests
import re


class CaptionGenerator:
    def __init__(self):
        self.templates = [
            "这谁顶得住啊",
            "我真的会谢",
            "今天也太离谱了吧",
            "行吧行吧我投降",
            "笑不活了",
            "我不理解但我尊重",
            "我的沉默震耳欲聋",
            "你礼貌吗",
            "我太难了",
            "你说得对，然后呢",
            "让子弹再飞一会儿",
        ]

        self.style_bias = {
            "cartoon": ["夸张到起飞", "卡通感拉满"],
            "hand-drawn": ["随手一画就很顶", "手绘感拿捏"],
            "anime": ["中二之魂燃了", "动漫感爆表"],
            "realistic": ["这也太真实了", "现实击中我"],
            "retro": ["复古滤镜开满", "像素风yyds"],
            "minimalist": ["极简但不简单", "少即是多"],
        }

        self.meme_addons = [
            "懂的都懂",
            "别问，问就是",
            "离谱但合理",
            "一整个无语住了",
            "我真的会栓Q",
        ]
        self.llm_url = os.getenv("CAPTION_LLM_URL", "").strip()
        self.llm_key = os.getenv("CAPTION_LLM_API_KEY", "").strip()
        self.llm_model = os.getenv("CAPTION_LLM_MODEL", "").strip()
        self.llm_temperature = float(os.getenv("CAPTION_LLM_TEMPERATURE", "0.9"))
        self.llm_timeout = int(os.getenv("CAPTION_LLM_TIMEOUT", "30"))
        self.llm_debug = os.getenv("CAPTION_LLM_DEBUG", "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        if self.llm_url:
            print(f"📝 Caption LLM enabled: model={self.llm_model or 'default'}")
        else:
            print("📝 Caption LLM disabled (CAPTION_LLM_URL not set)")

    def generate(self, prompt: str, style: str = "cartoon", meme_mode: bool = False) -> str:
        if self._llm_enabled():
            try:
                captions = self._call_llm(prompt, style, meme_mode, count=1)
                if captions:
                    return captions[0]
            except Exception as e:
                print(f"⚠️ Caption LLM failed: {e}")

        base = random.choice(self.templates)
        bias = random.choice(self.style_bias.get(style, [])) if self.style_bias.get(style) else ""
        addon = random.choice(self.meme_addons) if meme_mode else ""

        parts = [base]
        if bias:
            parts.append(bias)
        if addon:
            parts.append(addon)

        # 融合用户输入关键词（简单拼接避免过长）
        keyword = prompt.strip()
        if keyword and len(keyword) <= 8:
            parts.insert(0, keyword)

        return "，".join(parts)

    def generate_batch(
        self, prompt: str, style: str = "cartoon", meme_mode: bool = False, count: int = 3
    ) -> list[str]:
        count = max(1, min(6, int(count)))
        if self._llm_enabled():
            try:
                captions = self._call_llm(prompt, style, meme_mode, count=count)
                if captions:
                    return captions[:count]
            except Exception as e:
                print(f"⚠️ Caption LLM failed: {e}")

        results: list[str] = []
        seen = set()
        attempts = 0

        while len(results) < count and attempts < count * 4:
            caption = self.generate(prompt, style, meme_mode)
            attempts += 1
            if caption in seen:
                continue
            seen.add(caption)
            results.append(caption)

        return results

    def _llm_enabled(self) -> bool:
        return bool(self.llm_url)

    def _call_llm(
        self, prompt: str, style: str, meme_mode: bool, count: int = 1
    ) -> list[str]:
        count = max(1, min(6, int(count)))
        headers = {"Content-Type": "application/json"}
        if self.llm_key:
            headers["Authorization"] = f"Bearer {self.llm_key}"

        system = (
            "你是一个中文表情包文案生成器。输出简短、有梗、口语化的文案。"
            "不要添加引号、不要编号、不要解释。"
        )
        user = (
            f"用户提示词：{prompt}\n"
            f"风格：{style}\n"
            f"热梗模式：{'是' if meme_mode else '否'}\n"
            f"请输出 {count} 条文案，每条一行，长度<=12字。"
        )

        payload = {
            "model": self.llm_model or "default",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.llm_temperature,
            "max_tokens": 160,
        }

        response = requests.post(
            self.llm_url, headers=headers, json=payload, timeout=self.llm_timeout
        )
        if response.status_code >= 400:
            body_preview = response.text[:800].replace("\n", " ")
            if self.llm_debug:
                print(f"❌ Caption LLM HTTP {response.status_code} body: {body_preview}")
        response.raise_for_status()
        data = response.json()

        content = ""
        if isinstance(data, dict):
            choices = data.get("choices") or []
            if choices:
                content = choices[0].get("message", {}).get("content", "")
            if not content:
                output = data.get("output") or {}
                output_choices = output.get("choices") or []
                if output_choices:
                    content = output_choices[0].get("message", {}).get("content", "")
            if not content:
                content = data.get("output_text") or data.get("text") or ""

        if not content:
            raise Exception("Empty LLM response")

        lines = re.split(r"[\r\n]+", content)
        cleaned = []
        for line in lines:
            line = line.strip()
            line = re.sub(r"^[\-\*\d\.\)\s]+", "", line)
            if line:
                cleaned.append(line)

        return cleaned[:count]


caption_generator = CaptionGenerator()
