import React, { useMemo, useState } from 'react';
import InputComponent from './components/InputComponent';
import { StyleSelector, StyleType } from './components/StyleSelector';
import PreviewComponent from './components/PreviewComponent';
import DownloadComponent from './components/DownloadComponent';
import HistoryComponent, { HistoryItem } from './components/HistoryComponent';
import { IconMask, IconHeart } from './components/Icons';
import { useMemeGenerator } from './hooks/useMemeGenerator';

const isProviderEnabled = (value: string) => value.toLowerCase() === 'true';

const App: React.FC = () => {
  const {
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
  } = useMemeGenerator();

  const [historyQuery, setHistoryQuery] = useState('');
  const [historyProvider, setHistoryProvider] = useState('all');
  const [historyFavoritesOnly, setHistoryFavoritesOnly] = useState(false);

  const handleSelectHistory = (item: HistoryItem) => {
    selectHistoryItem(item);
  };

  const handleSelectCaption = (caption: string) => {
    setSelectedCaption(caption);
    setPrompt(caption);
  };

  const promptPresets = [
    '我太难了',
    '打工人',
    '老板让我加班',
    '笑不活了',
    '无语住了',
    '离谱但合理',
  ];

  const providerOptions = useMemo(() => {
    const set = new Set<string>();
    history.forEach((item) => {
      if (item.provider) set.add(item.provider);
    });
    return ['all', ...Array.from(set)];
  }, [history]);

  const filteredHistory = useMemo(() => {
    return history.filter((item) => {
      if (historyFavoritesOnly && !favoriteIds.includes(item.id)) return false;
      if (historyProvider !== 'all' && item.provider !== historyProvider) return false;
      if (historyQuery.trim()) {
        const q = historyQuery.trim().toLowerCase();
        const text = `${item.prompt} ${item.optimizedPrompt}`.toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });
  }, [history, historyFavoritesOnly, favoriteIds, historyProvider, historyQuery]);

  const clipdropStatus = providers.find((item) => item.name === 'clipdrop');
  const enabledProvidersCount = providers.filter((item) => isProviderEnabled(item.enabled)).length;
  const currentTemplate = templates.find((item) => item.id === selectedTemplate);
  const activeProviderLabel =
    provider === 'template'
      ? `模板：${currentTemplate?.name || selectedTemplate || 'unknown'}`
      : provider || '未生成';

  let previewNotice: string | undefined;
  if (provider === 'template') {
    previewNotice = '当前使用模板模式：默认在模板上叠加文案；接入 A1111 后可启用 img2img 风格化。';
  } else if (isMock) {
    previewNotice =
      '当前所有真实模型不可用，已使用 Mock 占位图。请配置 CLIPDROP_API_KEY 或 SD_WEBUI_URL。';
  } else if (provider && provider !== 'clipdrop' && clipdropStatus && !isProviderEnabled(clipdropStatus.enabled)) {
    previewNotice = `Clipdrop 未配置或不可用，已切换到 ${provider}。`;
  }

  return (
    <div className="app">
      <header className="header">
        <h1>
          <IconMask className="header-icon" aria-hidden />
          AI 表情包生成器
        </h1>
        <p>输入一句话，快速生成可下载、可超清、可复用的梗图</p>
        <div className="hero-status-row">
          <span className={`hero-pill ${isMock ? 'warn' : ''}`}>
            当前来源：{isMock ? 'Mock 占位' : activeProviderLabel}
          </span>
          <span className="hero-pill">
            模型可用：{enabledProvidersCount}/{providers.length || 0}
          </span>
          <span className="hero-pill">历史：{history.length} 条</span>
        </div>
      </header>

      <main className="main-content">
        <div className="left-panel">
          <div className="section input-section">
            <InputComponent
              value={prompt}
              onChange={setPrompt}
              onSubmit={generateMeme}
              isLoading={isLoading}
              optimizedPrompt={optimizedPrompt}
              promptPresets={promptPresets}
              onSelectPreset={(value) => setPrompt(value)}
              autoCaption={autoCaption}
              captionSuggestions={captionSuggestions}
              selectedCaption={selectedCaption}
              onSelectCaption={handleSelectCaption}
              onRefreshCaptions={fetchCaptions}
              captionLoading={captionLoading}
              captionError={captionError}
            />
          </div>

          <div className="section config-section">
            <h3>生成配置</h3>
            <p className="section-subtitle">
              当前配置会自动记忆，下次打开可直接延续。
            </p>
            <div className="config-row">
              <label className="config-label">
                <input
                  type="checkbox"
                  checked={autoCaption}
                  onChange={(e) => {
                    const next = e.target.checked;
                    setAutoCaption(next);
                    if (next) fetchCaptions();
                  }}
                  aria-label="自动文案"
                />
                自动文案
              </label>
              <span className="config-tip">
                {autoCaption ? '将优先使用候选文案' : '将直接使用你的输入作为文案'}
              </span>
            </div>
            <div className="config-row">
              <label className="config-label">
                <input
                  type="checkbox"
                  checked={memeMode}
                  onChange={(e) => setMemeMode(e.target.checked)}
                  aria-label="热梗模式"
                />
                热梗模式
              </label>
              <span className="config-tip">
                {memeMode ? '强化网络梗语气' : '关闭后文案更中性'}
              </span>
            </div>
            <div className="config-row">
              <span id="num-variants-label">变体数量</span>
              <input
                type="range"
                min={1}
                max={6}
                step={1}
                value={numVariants}
                onChange={(e) => setNumVariants(Number(e.target.value))}
                aria-labelledby="num-variants-label"
              />
              <span className="config-value">{numVariants}</span>
            </div>
          </div>

          <div className="section template-section">
            <h3>模板库</h3>
            <p className="template-hint">
              不选模板时走纯 AI 生图；选模板时默认在模板上叠加文案。
            </p>
            {templatesError && <p className="template-error">{templatesError}</p>}
            <div className="template-grid">
              <button
                type="button"
                className={`template-item ${selectedTemplate === null ? 'active' : ''}`}
                onClick={() => setSelectedTemplate(null)}
                aria-pressed={selectedTemplate === null}
                aria-label="选择 AI 生成"
              >
                <div className="template-placeholder">AI</div>
                <span>AI 生成</span>
              </button>
              {templates.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`template-item ${selectedTemplate === item.id ? 'active' : ''}`}
                  onClick={() => setSelectedTemplate(item.id)}
                  aria-pressed={selectedTemplate === item.id}
                  aria-label={`选择模板 ${item.name}`}
                >
                  <img src={item.previewUrl} alt={item.name} />
                  <span>{item.name}</span>
                </button>
              ))}
            </div>
            {selectedTemplate && currentTemplate && (
              <p className="template-meta">
                已选模板：{currentTemplate.name}
              </p>
            )}
          </div>

          <div className="section style-section">
            <StyleSelector
              selectedStyle={style}
              onStyleChange={(s) => setStyle(s as StyleType)}
              styleStrength={styleStrength}
              onStyleStrengthChange={setStyleStrength}
            />
          </div>

          <div className="section preview-section">
            <PreviewComponent
              imageUrl={imageUrl}
              isLoading={isLoading}
              error={error}
              provider={provider}
              isMock={isMock}
              notice={previewNotice}
            />
            {images.length > 1 && (
              <div className="variants-section">
                <h4>变体选择</h4>
                <div className="variants-grid">
                  {images.map((item) => (
                    <button
                      key={item.id}
                      type="button"
                      className={`variant-item ${
                        selectedImage?.id === item.id ? 'active' : ''
                      }`}
                      onClick={() => selectVariant(item)}
                      aria-pressed={selectedImage?.id === item.id}
                      aria-label={`选择变体 ${item.variantIndex ?? 0}`}
                    >
                      <img src={item.imageUrl} alt={`变体${item.variantIndex || 0}`} />
                    </button>
                  ))}
                </div>
              </div>
            )}
            {imageUrl && !isLoading && (
              <DownloadComponent
                imageUrl={imageUrl}
                upscaledImageUrl={upscaledImageUrl}
                onUpscale={upscaleImage}
                upscaling={upscaling}
                upscaleError={upscaleError}
              />
            )}
          </div>
        </div>

        <div className="right-panel">
          <div className="section provider-section">
            <h3>可用模型</h3>
            {providersError && <p className="provider-error">{providersError}</p>}
            {!providersError && providers.length === 0 && (
              <p className="provider-empty">未获取到可用模型状态</p>
            )}
            {providers.map((item) => (
              <div
                key={item.name}
                className={`provider-item ${
                  provider === item.name && !isMock ? 'active' : ''
                }`}
              >
                <span className="provider-name">{item.name}</span>
                <span className={`provider-status ${isProviderEnabled(item.enabled) ? 'ok' : 'bad'}`}>
                  {isProviderEnabled(item.enabled) ? '可用' : '不可用'}
                </span>
                <span className="provider-detail">{item.detail}</span>
              </div>
            ))}
          </div>
          <div className="section history-section">
            <div className="history-controls">
              <input
                type="text"
                placeholder="搜索历史..."
                value={historyQuery}
                onChange={(e) => setHistoryQuery(e.target.value)}
              />
              <select
                value={historyProvider}
                onChange={(e) => setHistoryProvider(e.target.value)}
              >
                {providerOptions.map((item) => (
                  <option key={item} value={item}>
                    {item === 'all' ? '全部来源' : item}
                  </option>
                ))}
              </select>
              <label className="history-fav-toggle">
                <input
                  type="checkbox"
                  checked={historyFavoritesOnly}
                  onChange={(e) => setHistoryFavoritesOnly(e.target.checked)}
                />
                仅收藏
              </label>
            </div>
            <HistoryComponent
              history={filteredHistory}
              onSelect={handleSelectHistory}
              onDelete={deleteHistoryItem}
              favoriteIds={favoriteIds}
              onToggleFavorite={toggleFavorite}
            />
          </div>
        </div>
      </main>

      <footer className="footer">
        <p>Powered by AI • Made with <IconHeart className="footer-heart" aria-hidden /> </p>
      </footer>
    </div>
  );
};

export default App;
