const API_BASE = '/api';

export interface GenerateRequest {
  prompt: string;
  style: string;
  styleStrength?: number;
  numVariants?: number;
  templateId?: string | null;
  memeMode?: boolean;
  addTextBubble?: boolean;
  text?: string;
}

export interface GeneratedImage {
  id: string;
  imageUrl: string;
  createdAt: string;
  provider?: string;
  isMock?: boolean;
  variantIndex?: number;
}

export interface GenerateResponse {
  success: boolean;
  id?: string;
  imageUrl: string;
  optimizedPrompt: string;
  createdAt?: string;
  provider?: string;
  isMock?: boolean;
  images?: GeneratedImage[];
  error?: string;
}

export interface HistoryItem {
  id: string;
  prompt: string;
  optimizedPrompt: string;
  style: string;
  imageUrl: string;
  createdAt: string;
  provider?: string;
  isMock?: boolean;
  styleStrength?: number;
}

export interface TemplateItem {
  id: string;
  name: string;
  previewUrl: string;
  sourceUrl?: string;
  license?: string;
}

export interface ProviderStatus {
  name: string;
  enabled: string;
  detail: string;
}

class ApiService {
  async generateMeme(request: GenerateRequest): Promise<GenerateResponse> {
    const response = await fetch(`${API_BASE}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error('生成失败');
    }

    return response.json();
  }

  async getHistory(): Promise<HistoryItem[]> {
    const response = await fetch(`${API_BASE}/history`);
    if (!response.ok) {
      throw new Error('获取历史记录失败');
    }
    return response.json();
  }

  async deleteHistory(id: string): Promise<void> {
    const response = await fetch(`${API_BASE}/history/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      throw new Error('删除失败');
    }
  }

  async optimizePrompt(prompt: string): Promise<string> {
    const response = await fetch(`${API_BASE}/optimize-prompt`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      throw new Error('优化提示词失败');
    }

    const data = await response.json();
    return data.optimizedPrompt;
  }

  async getProviders(): Promise<ProviderStatus[]> {
    const response = await fetch(`${API_BASE}/providers`);
    if (!response.ok) {
      throw new Error('获取提供者状态失败');
    }
    const data = await response.json();
    return data.providers || [];
  }

  async getTemplates(): Promise<TemplateItem[]> {
    const response = await fetch(`${API_BASE}/templates`);
    if (!response.ok) {
      throw new Error('获取模板失败');
    }
    const data = await response.json();
    return data.templates || [];
  }

  async generateCaption(prompt: string, style: string, memeMode: boolean): Promise<string> {
    const response = await fetch(`${API_BASE}/caption`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, style, memeMode }),
    });

    if (!response.ok) {
      throw new Error('生成文案失败');
    }

    const data = await response.json();
    return data.caption || '';
  }

  async generateCaptionBatch(
    prompt: string,
    style: string,
    memeMode: boolean,
    count: number
  ): Promise<string[]> {
    const response = await fetch(`${API_BASE}/caption/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt, style, memeMode, count }),
    });

    if (!response.ok) {
      throw new Error('批量生成文案失败');
    }

    const data = await response.json();
    return data.captions || [];
  }

  async upscaleImage(imageUrl: string): Promise<string> {
    const response = await fetch(`${API_BASE}/upscale`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ imageUrl }),
    });

    if (!response.ok) {
      throw new Error('超清增强失败');
    }

    const data = await response.json();
    return data.imageUrl || '';
  }
}

export const apiService = new ApiService();
