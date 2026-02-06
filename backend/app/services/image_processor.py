"""
图片后处理服务
添加文字气泡、调整字体、位置、颜色等
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple


class ImageProcessor:
    """图片处理器"""

    def __init__(self):
        self.default_font_size = 32
        self.bubble_padding = 20
        self.text_padding = 10

    def add_text_bubble(
        self,
        image_path: str,
        text: str,
        position: str = "bottom",
        font_size: Optional[int] = None,
        font_color: Tuple[int, int, int] = (0, 0, 0),
        bubble_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> str:
        """
        在图片上添加文字气泡

        Args:
            image_path: 图片路径
            text: 要添加的文字
            position: 气泡位置 ("top", "bottom", "center")
            font_size: 字体大小
            font_color: 字体颜色 (R, G, B)
            bubble_color: 气泡背景颜色 (R, G, B)

        Returns:
            处理后的图片路径
        """
        # 打开图片
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        # 获取字体
        font = self._get_font(font_size or self.default_font_size)

        # 自动换行与字号自适应
        max_bubble_width = int(image.size[0] * 0.8)
        max_bubble_height = int(image.size[1] * 0.3)
        font, lines, text_width, text_height = self._fit_text(
            draw, text, font, max_bubble_width, max_bubble_height
        )

        # 计算气泡尺寸
        bubble_width = text_width + self.text_padding * 2
        bubble_height = text_height + self.text_padding * 2

        # 根据位置计算气泡坐标
        img_width, img_height = image.size
        if position == "top":
            bubble_x = (img_width - bubble_width) // 2
            bubble_y = 20
        elif position == "bottom":
            bubble_x = (img_width - bubble_width) // 2
            bubble_y = img_height - bubble_height - 20
        else:  # center
            bubble_x = (img_width - bubble_width) // 2
            bubble_y = (img_height - bubble_height) // 2

        # 绘制圆角矩形气泡
        self._draw_rounded_rectangle(
            draw,
            (bubble_x, bubble_y, bubble_x + bubble_width, bubble_y + bubble_height),
            bubble_color,
            radius=15,
        )

        # 绘制文字（支持多行，带描边提升可读性）
        text_x = bubble_x + self.text_padding
        text_y = bubble_y + self.text_padding
        line_height = self._get_text_height(draw, "测试", font)
        for i, line in enumerate(lines):
            y = text_y + i * (line_height + 4)
            draw.text(
                (text_x, y),
                line,
                fill=font_color,
                font=font,
                stroke_width=2,
                stroke_fill=(255, 255, 255),
            )

        # 保存图片
        filename = f"processed_{os.path.basename(image_path)}"
        filepath = os.path.join(
            os.path.dirname(image_path),
            filename,
        )
        image.save(filepath)

        return filepath

    def _get_font(self, size: int):
        """获取字体"""
        try:
            # 尝试使用系统字体
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",
                "/System/Library/Fonts/Hiragino Sans GB.ttc",
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/SF Pro.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            ]
            env_font = os.getenv("MEME_FONT_PATH")
            if env_font:
                font_paths.insert(0, env_font)
            for font_path in font_paths:
                if os.path.exists(font_path):
                    return ImageFont.truetype(font_path, size)
        except Exception:
            pass

        # 回退到默认字体
        return ImageFont.load_default()

    def _draw_rounded_rectangle(
        self,
        draw,
        coords: Tuple[int, int, int, int],
        fill: Tuple[int, int, int],
        radius: int = 10,
    ):
        """绘制圆角矩形"""
        x1, y1, x2, y2 = coords

        # 绘制主体矩形（去掉四个角）
        draw.rectangle(
            [x1 + radius, y1, x2 - radius, y2],
            fill=fill,
        )
        draw.rectangle(
            [x1, y1 + radius, x2, y2 - radius],
            fill=fill,
        )

        # 绘制四个角
        draw.ellipse(
            [x1, y1, x1 + radius * 2, y1 + radius * 2],
            fill=fill,
        )
        draw.ellipse(
            [x2 - radius * 2, y1, x2, y1 + radius * 2],
            fill=fill,
        )
        draw.ellipse(
            [x1, y2 - radius * 2, x1 + radius * 2, y2],
            fill=fill,
        )
        draw.ellipse(
            [x2 - radius * 2, y2 - radius * 2, x2, y2],
            fill=fill,
        )

        # 绘制边框
        draw.arc(
            [x1, y1, x1 + radius * 2, y1 + radius * 2],
            180,
            270,
            fill=fill,
        )
        draw.arc(
            [x2 - radius * 2, y1, x2, y1 + radius * 2],
            270,
            360,
            fill=fill,
        )
        draw.arc(
            [x1, y2 - radius * 2, x1 + radius * 2, y2],
            90,
            180,
            fill=fill,
        )
        draw.arc(
            [x2 - radius * 2, y2 - radius * 2, x2, y2],
            0,
            90,
            fill=fill,
        )

    def _wrap_text(self, draw, text: str, font: ImageFont.FreeTypeFont, max_width: int):
        lines = []
        current = ""
        for char in text:
            test = f"{current}{char}"
            if self._get_text_width(draw, test, font) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
        return lines

    def _get_text_width(self, draw, text: str, font: ImageFont.FreeTypeFont) -> int:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

    def _get_text_height(self, draw, text: str, font: ImageFont.FreeTypeFont) -> int:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[3] - bbox[1]

    def _fit_text(
        self,
        draw,
        text: str,
        font: ImageFont.FreeTypeFont,
        max_width: int,
        max_height: int,
    ):
        size = font.size if hasattr(font, "size") else self.default_font_size
        size = min(size, 40)
        while size >= 16:
            font = self._get_font(size)
            lines = self._wrap_text(draw, text, font, max_width - self.text_padding * 2)
            line_height = self._get_text_height(draw, "测试", font)
            text_height = len(lines) * line_height + (len(lines) - 1) * 4
            text_width = 0
            for line in lines:
                text_width = max(text_width, self._get_text_width(draw, line, font))
            if text_width <= max_width and text_height <= max_height:
                return font, lines, text_width, text_height
            size -= 2
        lines = self._wrap_text(draw, text, font, max_width - self.text_padding * 2)
        text_width = max(self._get_text_width(draw, line, font) for line in lines)
        text_height = len(lines) * self._get_text_height(draw, "测试", font)
        return font, lines, text_width, text_height


# 全局实例
image_processor = ImageProcessor()
