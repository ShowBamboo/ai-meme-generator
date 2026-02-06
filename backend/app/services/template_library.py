"""
模板库服务
提供真实梗图模板（本地图片）
"""

import os
from typing import List, Dict, Optional


class TemplateLibrary:
    def __init__(self):
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        project_root = os.path.dirname(backend_dir)
        static_dir = os.path.join(project_root, "static")
        self.template_dir = os.path.join(static_dir, "templates")
        os.makedirs(self.template_dir, exist_ok=True)

        self.templates: List[Dict[str, str]] = [
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
        return None


template_library = TemplateLibrary()
