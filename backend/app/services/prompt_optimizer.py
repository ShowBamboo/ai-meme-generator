"""
提示词优化服务
将用户输入的中文/英文提示词转换为更适合文生图模型的英文提示词
"""

import re
from typing import Dict

# 风格关键词映射
STYLE_KEYWORDS = {
    "cartoon": ["cartoon style", "comic style", "funny", "exaggerated", "vibrant colors"],
    "hand-drawn": ["hand-drawn", "sketch style", "rough lines", "artistic", "pencil drawing"],
    "anime": ["anime style", "manga style", "Japanese animation", "clean lines", "cel shaded"],
    "realistic": ["photorealistic", "realistic", "detailed", "high quality", "professional"],
    "retro": ["retro style", "pixel art", "8-bit", "vintage", "nostalgic"],
    "minimalist": ["minimalist", "simple", "clean design", "flat design", "modern"],
}

# 中文情感词到英文的映射
EMOTION_MAPPING = {
    "我太难了": "feeling overwhelmed and stressed, sad face, dramatic",
    "老板让我加班": "boss making me work overtime, tired, exhausted, frustrated",
    "开心": "happy, joyful, smiling, excited",
    "难过": "sad, crying, tearful, depressed",
    "生气": "angry, furious, irritated, annoyed",
    "惊讶": "surprised, shocked, amazed, astonished",
    "无语": "speechless, dumbfounded, exasperated",
    "崩溃": "breaking down, overwhelmed, desperate",
    "躺平": "lying down, relaxed, lazy, chill",
    "内卷": "working hard, competitive, stressed",
    "emo": "emotional, sad, melancholic, thoughtful",
    "打工人": "tired worker, office worker, exhausted",
    "摸鱼": "slacking off, relaxing, taking it easy",
    "真香": "eating delicious food, satisfied, happy",
    "裂开": "shocked, broken, devastated",
    "熊猫": "panda, cute, adorable, black and white",
    "猫": "cat, cute, adorable, furry",
    "狗": "dog, cute, adorable, loyal",
}


class PromptOptimizer:
    """提示词优化器"""

    def __init__(self):
        self.emotion_mapping = EMOTION_MAPPING
        self.style_keywords = STYLE_KEYWORDS

    async def optimize(
        self,
        prompt: str,
        style: str = "cartoon",
        strength: int = 2,
        meme_mode: bool = False,
    ) -> str:
        """
        优化用户输入的提示词

        Args:
            prompt: 用户原始输入
            style: 选择的风格
            strength: 风格强度 (1-3)
            meme_mode: 是否启用热梗风格

        Returns:
            优化后的英文提示词
        """
        # 1. 检测并替换中文情感词
        optimized = self._translate_emotions(prompt)

        # 2. 添加风格关键词
        optimized = self._add_style(optimized, style, strength)

        if meme_mode:
            optimized = self._add_meme_mode(optimized)

        # 3. 添加通用优化词
        optimized = self._add_general_quality(optimized)

        # 4. 清理和格式化
        optimized = self._clean_up(optimized)

        return optimized

    def _add_meme_mode(self, text: str) -> str:
        meme_words = [
            "internet meme",
            "viral",
            "humorous",
            "expressive reaction",
            "caption friendly",
            "bold emotions",
        ]
        return f"{text}, {', '.join(meme_words)}"

    def _translate_emotions(self, text: str) -> str:
        """翻译中文情感词到英文"""
        result = text
        for cn_word, en_words in self.emotion_mapping.items():
            # 精确匹配
            if cn_word in result:
                result = result.replace(cn_word, en_words)
        return result

    def _add_style(self, text: str, style: str, strength: int) -> str:
        """添加风格关键词"""
        style_words = self.style_keywords.get(style, self.style_keywords["cartoon"])
        strength = max(1, min(3, int(strength)))

        style_templates = {
            "cartoon": [
                "cartoon character",
                "bold outlines",
                "vibrant flat colors",
                "exaggerated expression",
            ],
            "hand-drawn": [
                "hand-drawn illustration",
                "sketchy lines",
                "paper texture",
                "casual doodle",
            ],
            "anime": [
                "anime illustration",
                "cel shading",
                "clean lineart",
                "expressive eyes",
            ],
            "realistic": [
                "photorealistic",
                "natural lighting",
                "high detail",
                "sharp focus",
            ],
            "retro": [
                "retro pixel art",
                "8-bit style",
                "limited color palette",
                "nostalgic vibe",
            ],
            "minimalist": [
                "minimalist illustration",
                "simple shapes",
                "clean background",
                "limited colors",
            ],
        }

        template_words = style_templates.get(style, style_templates["cartoon"])
        intensity_words = []
        if strength == 2:
            intensity_words = ["highly stylized", "strong style"]
        elif strength == 3:
            intensity_words = ["extremely stylized", "very strong style", "distinctive look"]

        composition_words = [
            "single character",
            "centered composition",
            "clean background",
            "meme sticker",
            "leave space for caption",
        ]

        combined = style_words + template_words + intensity_words + composition_words
        return f"{text}, {', '.join(combined)}"

    def _add_general_quality(self, text: str) -> str:
        """添加通用质量提升词"""
        quality_words = [
            "high resolution",
            "sharp focus",
            "detailed",
            "beautiful",
            "cute",
            "funny meme",
        ]
        return f"{text}, {', '.join(quality_words)}"

    def _clean_up(self, text: str) -> str:
        """清理和格式化"""
        # 移除多余空格
        text = re.sub(r"\s+", " ", text)
        # 确保首字母大写
        text = text.strip()
        return text


# 全局实例
prompt_optimizer = PromptOptimizer()
