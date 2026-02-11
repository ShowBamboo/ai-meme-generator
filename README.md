# AI 表情包生成器 (AI Meme Generator)

一个可本地运行、可演示、可继续扩展的 AI 表情包生成项目：
- 前端：React + TypeScript + Vite
- 后端：FastAPI + 多模型路由 + 图片后处理

## 已实现功能点

### 1) 核心生成链路
- 文案输入 -> 提示词优化 -> 模型生图 -> 文案气泡叠加 -> 结果预览
- 支持一键生成与回车快速生成（`Enter` 生成，`Shift + Enter` 换行）
- 生成配置会自动记忆（风格、强度、变体数、模板选择、热梗模式、自动文案）

### 2) 多模型与容灾
- 多提供方路由与优先级切换：`clipdrop / siliconflow / webui / pollinations / mock`
- 实时展示提供方可用状态（前端可见）
- 当真实模型不可用时自动回退到 `mock`，保证流程不中断

### 3) 风格与可控性
- 风格选择：卡通 / 手绘 / 动漫 / 真人 / 复古 / 极简
- 风格强度控制（1~3）
- 变体生成（1~6）并支持变体切换
- 热梗模式开关（增强网络梗语气）

### 4) 文案能力
- 自动文案开关（可直接使用输入，也可使用候选文案）
- 批量文案候选（换一批）
- 已支持接入外部 LLM（OpenAI-Compatible 接口）生成中文梗文案

### 5) 模板能力
- 模板库选择（可扩展为真实梗图素材）
- 模板模式下默认在模板图上叠加文案
- 可扩展接入 A1111 `img2img` 对模板进行风格化重绘
- 一键同步网络热梗模板（Imgflip）+ 支持粘贴图片 URL 下载到本地模板库

### 6) 图片增强与导出
- 超清增强入口（独立按钮，不是默认行为）
- 超清前后对比卡片（原图/超清分开展示）
- 下载原图、下载超清图、复制链接
- 分享入口（Twitter / 微博）

### 7) 历史与管理
- 历史记录展示、搜索、按来源筛选
- 收藏能力（本地）
- 历史记录快速“复用”回填当前编辑区
- 删除单条历史记录

### 8) 产品化 UI/交互（本次已优化）
- 头部状态胶囊：当前来源、可用模型数、历史条数
- 输入区状态提示：字符数、快捷键、清空按钮
- 配置区说明文案与即时状态反馈
- 提供方当前命中高亮、模板当前选择提示
- 历史区操作按钮更清晰（复用/收藏/删除）

## 项目结构

```text
ai-meme-generator/
├── frontend/                     # React 前端
│   ├── src/
│   │   ├── components/           # 业务组件
│   │   ├── hooks/useMemeGenerator.ts
│   │   ├── services/api.ts
│   │   ├── styles/index.css
│   │   └── App.tsx
│   └── vite.config.ts
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── routers/              # /api 路由
│   │   ├── services/             # 生成、文案、模板、超清等服务
│   │   ├── models/
│   │   └── main.py
│   ├── requirements.txt
│   └── static/
│       ├── templates/
│       └── uploads/
└── README.md
```

## 快速启动

### 前置要求
- Node.js 18+
- Python 3.9+（建议 3.10+）

> 注意：请使用 `python3 -m pip`，避免系统旧版 `pip` 或 Python2 包装器问题。

### 1) 启动后端

```bash
cd /Users/qiugonghai/meitu/ai-meme-generator/backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

# 至少配置一个真实提供方，示例：Clipdrop
export CLIPDROP_API_KEY="你的key"

# 可选：接入文案 LLM（示例：阿里云 DashScope 兼容接口）
# export CAPTION_LLM_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
# export CAPTION_LLM_MODEL="qwen-plus"
# export CAPTION_LLM_API_KEY="sk-..."

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：`http://localhost:8000`

### 2) 启动前端

```bash
cd /Users/qiugonghai/meitu/ai-meme-generator/frontend
npm install
npm run dev
```

前端地址：`http://localhost:3000`

## 关键环境变量

可参考根目录 `.env.example`：

- 生图提供方
  - `CLIPDROP_API_KEY`
  - `SD_WEBUI_URL`
  - `REPLICATE_API_TOKEN`
  - `HUGGINGFACE_API_TOKEN`
  - `POLLINATIONS_ENABLED`
- 提供方调度
  - `IMAGE_GENERATION_PROVIDER`
  - `IMAGE_GENERATION_PROVIDER_ORDER`
- 文案 LLM
  - `CAPTION_LLM_URL`
  - `CAPTION_LLM_API_KEY`
  - `CAPTION_LLM_MODEL`
  - `CAPTION_LLM_TEMPERATURE`
  - `CAPTION_LLM_TIMEOUT`
  - `CAPTION_LLM_DEBUG`

## API 概览

- `POST /api/generate`：生成表情包（支持风格、模板、变体、文案）
- `POST /api/optimize-prompt`：仅优化提示词
- `GET /api/providers`：查询提供方状态
- `GET /api/templates`：查询模板列表
- `POST /api/templates/sync`：同步热梗模板（`source=imgflip`）或下载 URL 模板（`source=urls`）
- `POST /api/caption`：单条文案生成
- `POST /api/caption/batch`：批量文案候选
- `POST /api/upscale`：超清增强
- `GET /api/history`：历史记录
- `DELETE /api/history/{meme_id}`：删除历史记录

## 演示建议（给同事）

1. 用 `GET /api/providers` 先展示模型状态（确认不是 mock-only）。
2. 现场输入一句梗文案，切换不同风格和强度，生成 2~4 个变体。
3. 打开自动文案并“换一批”，展示候选差异。
4. 切换模板模式，展示模板叠字链路。
5. 点击“超清增强”，展示原图/超清对比与下载。
6. 在历史区演示搜索、筛选、收藏、复用、删除。

## 常见问题

### 1) 为什么会走 mock？
- 真实提供方调用失败（配额、网络、参数、服务异常）会自动回退。
- 建议先查 `GET /api/providers`，再看后端日志中的失败原因。

### 2) 文案像默认模板，没走 LLM？
- 检查 `CAPTION_LLM_URL / CAPTION_LLM_MODEL / CAPTION_LLM_API_KEY`。
- 启动日志应看到 `Caption LLM enabled`。

### 3) 安装依赖报 `Python 2.7` 或 `old script wrapper`？
- 用 `python3 -m pip install -r requirements.txt`。
- 推荐启用虚拟环境后安装。

## 技术栈

- 前端：React 18、TypeScript、Vite、CSS
- 后端：FastAPI、Pydantic、Pillow、Requests
- 可选模型：Clipdrop、SiliconFlow、A1111 WebUI、Pollinations、外部文案 LLM

## License

MIT
