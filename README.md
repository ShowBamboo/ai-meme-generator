# AI 表情包生成器 (AI Meme Generator)

一个智能表情包生成器，用户输入一句话，AI 自动生成专属表情包。

## 功能特性

- 🎨 **智能提示词优化** - AI 自动优化用户输入，生成更适合文生图的提示词
- 🖼️ **多种风格选择 + 强度** - 卡通、手绘、动漫、真人、复古、极简等多种风格与强度控制
- 🔥 **热梗模式** - 加强“梗图语气”的提示词优化
- ✍️ **自动文案 + 候选池** - 一键生成多条文案候选并选择使用
- 🧠 **文案模型可接入** - 可配置外部模型生成更真实的梗文案
- 🧪 **模板库 + 提示词改图** - 模板库选择 +（可选）本地 A1111 img2img 风格化
- ✨ **图片后处理** - 自动添加文字气泡、自动换行、字号自适应、描边增强可读性
- 🧩 **多变体生成** - 一次生成多张变体并切换预览
- 🔎 **超清增强入口** - 独立入口触发 Clipdrop 超清增强并支持对比
- 📥 **下载与分享** - 支持下载图片，生成分享链接
- 📜 **历史记录 + 搜索/收藏** - 历史可检索、筛选与收藏（本地）

## 项目结构

```
ai-meme-generator/
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── components/       # 组件
│   │   │   ├── InputComponent.tsx      # 输入组件
│   │   │   ├── StyleSelector.tsx       # 风格选择器
│   │   │   ├── PreviewComponent.tsx    # 预览组件
│   │   │   ├── DownloadComponent.tsx   # 下载组件
│   │   │   └── HistoryComponent.tsx    # 历史记录
│   │   ├── hooks/            # 自定义 Hooks
│   │   │   └── useMemeGenerator.ts
│   │   ├── services/         # API 服务
│   │   │   └── api.ts
│   │   ├── styles/           # 样式文件
│   │   │   └── index.css
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                  # Python 后端
│   ├── app/
│   │   ├── routers/          # API 路由
│   │   │   ├── generate.py   # 生成接口
│   │   │   └── history.py    # 历史记录接口
│   │   ├── services/         # 服务层
│   │   │   ├── prompt_optimizer.py    # 提示词优化
│   │   │   ├── image_generator.py     # 图片生成
│   │   │   └── image_processor.py     # 图片后处理
│   │   ├── models/           # 数据模型
│   │   │   └── meme.py
│   │   └── main.py           # FastAPI 应用入口
│   ├── requirements.txt
│   └── static/               # 静态文件
│       └── uploads/          # 上传目录
│
└── README.md
```

## 快速开始

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端将在 `http://localhost:3000` 启动

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 `http://localhost:8000` 启动

### 环境变量

参考 `.env.example` 配置环境变量（如 `CLIPDROP_API_KEY` 或 `SD_WEBUI_URL`）。

## API 接口

### 生成表情包

```
POST /api/generate
Content-Type: application/json

{
  "prompt": "我太难了",
  "style": "cartoon",
  "addTextBubble": true,
  "text": "我太难了"
}
```

响应:
```json
{
  "success": true,
  "imageUrl": "/static/uploads/meme-xxx.png",
  "optimizedPrompt": "feeling overwhelmed and stressed, sad face, cartoon style..."
}
```

### 获取历史记录

```
GET /api/history
```

### 删除历史记录

```
DELETE /api/history/{meme_id}
```

### 优化提示词

```
POST /api/optimize-prompt
Content-Type: application/json

{
  "prompt": "我太难了"
}
```

## 技术栈

### 前端
- React 18
- TypeScript
- Vite
- CSS3 (现代化样式)

### 后端
- FastAPI
- Python 3.10+
- Stable Diffusion (可选)
- Pillow (图片处理)

## 注意事项

1. **Stable Diffusion 模型**: 支持本地 A1111 WebUI（`SD_WEBUI_URL`），无需付费即可生图
2. **Clipdrop**: 支持免费额度生图（`CLIPDROP_API_KEY`），默认优先使用
2. **字体支持**: 图片处理支持系统字体，中文字体需要系统支持
3. **生产部署**: 建议使用 Gunicorn + Uvicorn 部署后端

## License

MIT
