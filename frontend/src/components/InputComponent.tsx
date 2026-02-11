import React from 'react';
import { IconSparkle } from './Icons';

interface InputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  isLoading: boolean;
  optimizedPrompt?: string;
  promptPresets: string[];
  onSelectPreset: (value: string) => void;
  autoCaption: boolean;
  captionSuggestions: string[];
  selectedCaption: string | null;
  onSelectCaption: (caption: string) => void;
  onRefreshCaptions: () => void;
  captionLoading: boolean;
  captionError?: string;
}

const InputComponent: React.FC<InputProps> = ({
  value,
  onChange,
  onSubmit,
  isLoading,
  optimizedPrompt,
  promptPresets,
  onSelectPreset,
  autoCaption,
  captionSuggestions,
  selectedCaption,
  onSelectCaption,
  onRefreshCaptions,
  captionLoading,
  captionError
}) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  const charsLeft = Math.max(0, 200 - value.length);

  return (
    <div className="input-section">
      <div className="prompt-presets">
        {promptPresets.map((item) => (
          <button
            key={item}
            className="preset-chip"
            type="button"
            onClick={() => onSelectPreset(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="input-container">
        <div className="input-meta">
          <span>回车生成，Shift + 回车换行</span>
          <span className={charsLeft < 20 ? 'danger' : ''}>剩余 {charsLeft} 字</span>
        </div>
        <textarea
          className="prompt-input"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入你的创意，例如：'我太难了'、'老板让我加班'..."
          rows={3}
          maxLength={200}
          disabled={isLoading}
        />
        <div className="input-actions">
          <button
            type="button"
            className="ghost-btn"
            onClick={() => onChange('')}
            disabled={isLoading || !value}
          >
            清空
          </button>
          <button
            type="button"
            className="generate-btn"
            onClick={onSubmit}
            disabled={isLoading || !value.trim()}
            aria-busy={isLoading}
          >
            {isLoading ? (
              '生成中...'
            ) : (
              <>
                <IconSparkle className="btn-icon" /> 生成表情包
              </>
            )}
          </button>
        </div>
      </div>

      {autoCaption && (
        <div className="caption-lab">
          <div className="caption-header">
            <span>自动文案候选</span>
            <button
              type="button"
              className="caption-refresh"
              onClick={onRefreshCaptions}
              disabled={captionLoading}
            >
              {captionLoading ? '生成中...' : '换一批'}
            </button>
          </div>
          {captionError && <p className="caption-error">{captionError}</p>}
          {!captionError && !captionLoading && captionSuggestions.length === 0 && (
            <p className="caption-empty">点击“换一批”生成文案候选</p>
          )}
          <div className="caption-list">
            {captionSuggestions.map((caption) => (
              <button
                key={caption}
                type="button"
                className={`caption-item ${selectedCaption === caption ? 'active' : ''}`}
                onClick={() => onSelectCaption(caption)}
              >
                {caption}
              </button>
            ))}
          </div>
        </div>
      )}

      {optimizedPrompt && (
        <div className="optimized-prompt">
          <span className="label">AI 优化后的提示词：</span>
          <p>{optimizedPrompt}</p>
        </div>
      )}
    </div>
  );
};

export default InputComponent;
