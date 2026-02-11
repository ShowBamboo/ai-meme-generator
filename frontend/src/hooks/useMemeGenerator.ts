import { useState, useCallback, useEffect } from 'react';
import {
  apiService,
  GenerateRequest,
  ProviderStatus,
  GeneratedImage,
  TemplateItem,
} from '../services/api';
import { HistoryItem } from '../components/HistoryComponent';
import { StyleType } from '../components/StyleSelector';

const SETTINGS_KEY = 'meme_generator_settings';

interface SavedSettings {
  style: StyleType;
  styleStrength: number;
  numVariants: number;
  memeMode: boolean;
  autoCaption: boolean;
  selectedTemplate: string | null;
}

const getSavedSettings = (): SavedSettings | null => {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as SavedSettings;
  } catch {
    return null;
  }
};

export const useMemeGenerator = () => {
  const savedSettings = getSavedSettings();

  const [prompt, setPrompt] = useState('');
  const [optimizedPrompt, setOptimizedPrompt] = useState('');
  const [style, setStyle] = useState<StyleType>(savedSettings?.style || 'cartoon');
  const [styleStrength, setStyleStrength] = useState<number>(savedSettings?.styleStrength || 2);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [images, setImages] = useState<GeneratedImage[]>([]);
  const [selectedImage, setSelectedImage] = useState<GeneratedImage | null>(null);
  const [provider, setProvider] = useState<string | undefined>();
  const [isMock, setIsMock] = useState<boolean | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | undefined>();
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [providersError, setProvidersError] = useState<string | undefined>();
  const [templates, setTemplates] = useState<TemplateItem[]>([]);
  const [templatesError, setTemplatesError] = useState<string | undefined>();
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(
    savedSettings?.selectedTemplate ?? null
  );
  const [templateSyncing, setTemplateSyncing] = useState<boolean>(false);
  const [templateSyncMessage, setTemplateSyncMessage] = useState<string | undefined>();
  const [templateSyncError, setTemplateSyncError] = useState<string | undefined>();
  const [numVariants, setNumVariants] = useState<number>(savedSettings?.numVariants || 1);
  const [memeMode, setMemeMode] = useState<boolean>(savedSettings?.memeMode || false);
  const [autoCaption, setAutoCaption] = useState<boolean>(savedSettings?.autoCaption || false);
  const [captionSuggestions, setCaptionSuggestions] = useState<string[]>([]);
  const [selectedCaption, setSelectedCaption] = useState<string | null>(null);
  const [captionLoading, setCaptionLoading] = useState<boolean>(false);
  const [captionError, setCaptionError] = useState<string | undefined>();
  const [upscaledImageUrl, setUpscaledImageUrl] = useState<string | null>(null);
  const [upscaling, setUpscaling] = useState<boolean>(false);
  const [upscaleError, setUpscaleError] = useState<string | undefined>();
  const [favoriteIds, setFavoriteIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('meme_favorites');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    let isMounted = true;
    apiService
      .getHistory()
      .then((items) => {
        if (isMounted) setHistory(items);
      })
      .catch(() => {
        if (isMounted) setHistory([]);
      });

    apiService
      .getProviders()
      .then((items) => {
        if (isMounted) setProviders(items);
      })
      .catch((err) => {
        if (isMounted) {
          setProviders([]);
          setProvidersError(err instanceof Error ? err.message : '获取提供者状态失败');
        }
      });

    apiService
      .getTemplates()
      .then((items) => {
        if (isMounted) setTemplates(items);
      })
      .catch((err) => {
        if (isMounted) {
          setTemplates([]);
          setTemplatesError(err instanceof Error ? err.message : '获取模板失败');
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    const settings: SavedSettings = {
      style,
      styleStrength,
      numVariants,
      memeMode,
      autoCaption,
      selectedTemplate,
    };
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  }, [style, styleStrength, numVariants, memeMode, autoCaption, selectedTemplate]);

  const fetchCaptions = useCallback(async () => {
    if (!prompt.trim()) return;
    setCaptionLoading(true);
    setCaptionError(undefined);
    try {
      const captions = await apiService.generateCaptionBatch(
        prompt.trim(),
        style,
        memeMode,
        3
      );
      setCaptionSuggestions(captions);
      setSelectedCaption(captions[0] || null);
    } catch (err) {
      setCaptionError(err instanceof Error ? err.message : '生成文案失败');
    } finally {
      setCaptionLoading(false);
    }
  }, [prompt, style, memeMode]);

  const generateMeme = useCallback(async () => {
    if (!prompt.trim()) return;

    setIsLoading(true);
    setError(undefined);

    try {
      const request: GenerateRequest = {
        prompt: prompt.trim(),
        style,
        styleStrength,
        numVariants,
        templateId: selectedTemplate,
        memeMode,
        addTextBubble: true,
        text: prompt.trim(),
      };

      if (autoCaption) {
        const caption =
          selectedCaption ||
          captionSuggestions[0] ||
          (await apiService.generateCaption(prompt.trim(), style, memeMode));
        request.text = caption;
        setSelectedCaption(caption);
      }

      const response = await apiService.generateMeme(request);

      if (response.success) {
        setOptimizedPrompt(response.optimizedPrompt);
        const responseImages = response.images || [];
        const primary = responseImages[0] || null;
        setSelectedImage(primary);
        setImages(responseImages);
        setImageUrl(primary?.imageUrl || response.imageUrl);
        setProvider(primary?.provider || response.provider);
        setIsMock(primary?.isMock ?? response.isMock);
        setUpscaledImageUrl(null);
        setUpscaleError(undefined);

        const newItem: HistoryItem = {
          id: response.id || Date.now().toString(),
          prompt: prompt.trim(),
          optimizedPrompt: response.optimizedPrompt,
          style,
          imageUrl: primary?.imageUrl || response.imageUrl,
          createdAt: response.createdAt || new Date().toISOString(),
          provider: primary?.provider || response.provider,
          isMock: primary?.isMock ?? response.isMock,
          styleStrength,
        };

        setHistory((prev) => [newItem, ...prev].slice(0, 20));
      } else {
        setError(response.error || '生成失败');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '生成失败');
    } finally {
      setIsLoading(false);
    }
  }, [
    prompt,
    style,
    styleStrength,
    numVariants,
    selectedTemplate,
    memeMode,
    autoCaption,
    selectedCaption,
    captionSuggestions,
  ]);

  const selectHistoryItem = useCallback((item: HistoryItem) => {
    setPrompt(item.prompt);
    setOptimizedPrompt(item.optimizedPrompt);
    setStyle(item.style as StyleType);
    setImageUrl(item.imageUrl);
    setProvider(item.provider);
    setIsMock(item.isMock);
    setStyleStrength(item.styleStrength ?? 2);
    setImages([]);
    setSelectedImage(null);
    setUpscaledImageUrl(null);
    setUpscaleError(undefined);
  }, []);

  const toggleFavorite = useCallback((id: string) => {
    setFavoriteIds((prev) => {
      const set = new Set(prev);
      if (set.has(id)) {
        set.delete(id);
      } else {
        set.add(id);
      }
      const next = Array.from(set);
      localStorage.setItem('meme_favorites', JSON.stringify(next));
      return next;
    });
  }, []);

  const selectVariant = useCallback((item: GeneratedImage) => {
    setSelectedImage(item);
    setImageUrl(item.imageUrl);
    setProvider(item.provider);
    setIsMock(item.isMock);
    setUpscaledImageUrl(null);
    setUpscaleError(undefined);
  }, []);

  const upscaleImage = useCallback(async () => {
    if (!imageUrl) return;
    setUpscaling(true);
    setUpscaleError(undefined);
    try {
      const url = await apiService.upscaleImage(imageUrl);
      setUpscaledImageUrl(url);
    } catch (err) {
      setUpscaleError(err instanceof Error ? err.message : '超清增强失败');
    } finally {
      setUpscaling(false);
    }
  }, [imageUrl]);

  const deleteHistoryItem = useCallback(async (id: string) => {
    try {
      await apiService.deleteHistory(id);
      setHistory((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      console.error('删除失败:', err);
    }
  }, []);

  const syncImgflipTemplates = useCallback(async () => {
    setTemplateSyncing(true);
    setTemplateSyncError(undefined);
    setTemplateSyncMessage(undefined);
    try {
      const data = await apiService.syncTemplates({
        source: 'imgflip',
        limit: 20,
      });
      setTemplates(data.templates || []);
      setTemplateSyncMessage(
        `已同步：新增 ${data.result.added}，跳过 ${data.result.skipped}，失败 ${data.result.failed}`
      );
    } catch (err) {
      setTemplateSyncError(err instanceof Error ? err.message : '同步模板失败');
    } finally {
      setTemplateSyncing(false);
    }
  }, []);

  const syncUrlTemplates = useCallback(async (urls: string[]) => {
    setTemplateSyncing(true);
    setTemplateSyncError(undefined);
    setTemplateSyncMessage(undefined);
    try {
      const data = await apiService.syncTemplates({
        source: 'urls',
        urls,
      });
      setTemplates(data.templates || []);
      setTemplateSyncMessage(
        `URL 同步完成：新增 ${data.result.added}，跳过 ${data.result.skipped}，失败 ${data.result.failed}`
      );
    } catch (err) {
      setTemplateSyncError(err instanceof Error ? err.message : 'URL 模板同步失败');
    } finally {
      setTemplateSyncing(false);
    }
  }, []);

  return {
    prompt,
    setPrompt,
    optimizedPrompt,
    style,
    setStyle,
    styleStrength,
    setStyleStrength,
    imageUrl,
    images,
    selectedImage,
    setSelectedImage,
    selectVariant,
    provider,
    isMock,
    isLoading,
    error,
    history,
    providers,
    providersError,
    templates,
    templatesError,
    selectedTemplate,
    setSelectedTemplate,
    templateSyncing,
    templateSyncMessage,
    templateSyncError,
    syncImgflipTemplates,
    syncUrlTemplates,
    numVariants,
    setNumVariants,
    memeMode,
    setMemeMode,
    autoCaption,
    setAutoCaption,
    captionSuggestions,
    selectedCaption,
    setSelectedCaption,
    captionLoading,
    captionError,
    fetchCaptions,
    upscaledImageUrl,
    upscaling,
    upscaleError,
    upscaleImage,
    favoriteIds,
    toggleFavorite,
    generateMeme,
    selectHistoryItem,
    deleteHistoryItem,
  };
};
