# 图像生成设置指南

## 概述

系统现在支持 **6 种图像生成方式**，按优先级：

1. **Clipdrop** - 免费额度，需要 API Key
2. **Local SD WebUI (AUTOMATIC1111)** - 免费，本地调用
3. **Replicate FLUX** - 最佳质量，需要 API Token（推荐）
4. **Hugging Face Router** - 高质量，需要 API Token
5. **Pollinations.ai** - 免费（视服务状态）
6. **Mock 生成** - 仅开发测试用

---

## 方案0: Clipdrop（免费额度）

**优点：**
- ✅ 有稳定的免费额度
- ✅ API 质量不错
- ✅ 集成简单

**获取 Key：**

1. 注册/登录 Clipdrop
2. 进入 API 控制台获取 Key

**设置环境变量：**

```bash
export CLIPDROP_API_KEY="your_key_here"
```

**启动后端：**

```bash
cd backend
CLIPDROP_API_KEY="your_key_here" uvicorn app.main:app --reload
```

---

## 方案1: 本地 SD WebUI（免费）

**优点：**
- ✅ 完全免费（本地模型）
- ✅ 质量可控（自行选择模型）
- ✅ 不依赖第三方服务稳定性

**前提：**
- 需要安装并启动 [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

**设置环境变量：**

```bash
export SD_WEBUI_URL="http://127.0.0.1:7860"
```

**可选参数：**

```bash
export SD_WEBUI_STEPS="20"
export SD_WEBUI_CFG="7"
export SD_WEBUI_SAMPLER="Euler a"
export SD_WEBUI_NEGATIVE="low quality, blurry, watermark"
```

**启动后端：**

```bash
cd backend
SD_WEBUI_URL="http://127.0.0.1:7860" uvicorn app.main:app --reload
```

---

## 方案1: Replicate + FLUX（推荐）

**优点：**
- ✅ FLUX 模型质量优秀
- ✅ 有免费试用额度（新用户通常有 $10+ 免费额度）
- ✅ 稳定可靠
- ✅ 生成速度快（4-8步）

**获取 Token：**

1. 访问 https://replicate.com/account/api-tokens
2. 创建 API Token
3. 复制 Token

**设置环境变量：**

```bash
export REPLICATE_API_TOKEN="your_token_here"
```

**启动后端：**

```bash
cd backend
REPLICATE_API_TOKEN="r8_..." uvicorn app.main:app --reload
```

**验证：**

后端日志应显示：
```
🤖 ReplicateGenerator initialized (FLUX.1-schnell)
🎨 ImageGenerator initialized
📊 Provider Priority:
   1. 🤖 Replicate FLUX (best quality, requires token)
      ✅ Token configured
```

---

## 方案2: Hugging Face Router

**优点：**
- ✅ 稳定可靠
- ✅ 支持多种模型
- ✅ 有免费额度（取决于模型）

**获取 Token：**

1. 访问 https://huggingface.co/settings/tokens
2. 创建新 Token（需要读取权限）

**设置环境变量：**

```bash
export HUGGINGFACE_API_TOKEN="your_token_here"
```

**启动后端：**

```bash
cd backend
HUGGINGFACE_API_TOKEN="hf_..." uvicorn app.main:app --reload
```

---

## 方案3: Pollinations.ai（免费）

⚠️ **当前状态：视服务状态而定**  
如遇到 502/503，请使用本地 SD WebUI 或其他付费方案。

**状态监控：**
- 可以访问 https://pollinations.ai 检查服务状态
- 或者查看 https://status.pollinations.ai

**当服务恢复后：**
- 无需任何配置，自动使用
- 完全免费，无需 Token

---

## 方案4: Mock 生成（仅开发测试）

如果所有 API 都不可用，系统会自动回退到 Mock 模式。

Mock 模式特点：
- 生成带有提示词文本的占位图
- 带有 "[MOCK]" 标记
- 仅用于前端 UI 测试

---

## 环境变量配置

| 变量 | 必填 | 说明 |
|------|------|------|
| `CLIPDROP_API_KEY` | 否 | Clipdrop API Key |
| `SD_WEBUI_URL` | 否 | 本地 A1111 服务地址 |
| `SD_WEBUI_STEPS` | 否 | 采样步数（默认 20） |
| `SD_WEBUI_CFG` | 否 | CFG Scale（默认 7） |
| `SD_WEBUI_SAMPLER` | 否 | 采样器（默认 Euler a） |
| `SD_WEBUI_DENOISE` | 否 | img2img 去噪强度（默认 0.55） |
| `SD_WEBUI_NEGATIVE` | 否 | 负面提示词 |
| `REPLICATE_API_TOKEN` | 否 | Replicate API Token（推荐设置） |
| `HUGGINGFACE_API_TOKEN` | 否 | Hugging Face API Token |
| `POLLINATIONS_ENABLED` | 否 | 是否启用 Pollinations (true/false, 默认 true) |
| `IMAGE_GENERATION_PROVIDER` | 否 | 强制指定 provider（如 clipdrop/webui/replicate/huggingface/pollinations/mock） |
| `IMAGE_GENERATION_PROVIDER_ORDER` | 否 | provider 优先级（逗号分隔） |

## 超清增强

新增 `POST /api/upscale`，使用 Clipdrop 超清增强（需要 `CLIPDROP_API_KEY`）。

## 文案模型接入（可选）

可接入外部文案模型接口，配置以下环境变量：

| 变量 | 说明 |
|------|------|
| `CAPTION_LLM_URL` | 模型接口地址（Chat Completions 兼容） |
| `CAPTION_LLM_API_KEY` | 模型接口 Key（如需要） |
| `CAPTION_LLM_MODEL` | 模型名称 |
| `CAPTION_LLM_TEMPERATURE` | 温度（默认 0.9） |
| `CAPTION_LLM_TIMEOUT` | 超时秒数（默认 30） |
| `CAPTION_LLM_DEBUG` | 开启调试日志（true/false） |

---

## 故障排除

### 1. Replicate 返回错误

**问题：** "Credit limit exceeded"
**解决：** 需要充值或使用其他免费额度

**问题：** "Model not found"
**解决：** 模型版本可能已更新，检查 https://replicate.com/black-forest-labs/FLUX.1-schnell

### 2. Hugging Face 返回 401

**解决：** Token 无效或已过期，重新创建 Token

### 3. Pollinations 返回 502

**说明：** 服务暂时不可用，这是他们服务器的问题
**解决：** 等待服务恢复，或使用 Replicate/Hugging Face 作为替代

---

## 验证

生成图片后检查：

1. **日志**：应显示使用的 Provider
2. **文件**：应在 `static/uploads/` 生成 PNG 文件
3. **大小**：应大于 5KB（真实图片，非 Mock 的 ~10KB 文本图）
4. **格式**：`file` 命令应显示 `PNG image data`

```bash
file static/uploads/meme_*.png
# 应输出: PNG image data, 512 x 512, 8-bit/color RGB
```

## 方案2: Hugging Face API（需要 Token）

如果你已有 Hugging Face Token，可以设置使用：

1. 获取 Token：
   - 访问 https://huggingface.co/settings/tokens
   - 创建新 Token（需要读取权限）

2. 设置环境变量：
   ```bash
   export HUGGINGFACE_API_TOKEN="your_token_here"
   ```

3. **可选**：设置使用 HF 作为主提供者：
   ```bash
   export IMAGE_GENERATION_PROVIDER="huggingface"
   ```

4. 重启后端

**说明：**
- 如果设置了 `HUGGINGFACE_API_TOKEN`，当 Pollinations.ai 失败时会自动回退到 Hugging Face
- 如果设置 `IMAGE_GENERATION_PROVIDER="huggingface"`，会优先使用 Hugging Face

---

## 方案3: Mock 生成（仅开发测试）

如果既没有网络，也无法访问 Pollinations，系统会使用 Mock 模式生成占位图。

Mock 模式特点：
- 显示提示词文本
- 带有 "[MOCK]" 标记
- 仅用于前端 UI 测试

---

## 环境变量配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `IMAGE_GENERATION_PROVIDER` | `pollinations` | 生成提供者：`pollinations` 或 `huggingface` |
| `POLLINATIONS_API_URL` | `https://image.pollinations.ai/prompt` | Pollinations API 地址 |
| `HUGGINGFACE_API_TOKEN` | 无 | Hugging Face Token（可选） |

---

## 验证

生成一张图片，检查：

1. **日志**：应显示 `🌻 PollinationsGenerator initialized`
2. **图片**：应在 `static/uploads/` 目录生成真实图片（非文本）
3. **内容**：图片应显示与提示词相关的图像内容
