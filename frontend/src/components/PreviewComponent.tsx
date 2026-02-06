import React from 'react';
import { IconEmpty, IconSad } from './Icons';

interface PreviewProps {
  imageUrl: string | null;
  isLoading: boolean;
  error?: string;
  provider?: string;
  isMock?: boolean;
  notice?: string;
}

const PreviewComponent: React.FC<PreviewProps> = ({
  imageUrl,
  isLoading,
  error,
  provider,
  isMock,
  notice
}) => {
  if (isLoading) {
    return (
      <div className="preview-section">
        <div className="preview-container loading">
          <div className="loading-spinner"></div>
          <p>AI 正在创作中...</p>
          <span>这可能需要几秒钟时间</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preview-section">
        <div className="preview-container error">
          <IconSad className="error-icon" aria-hidden />
          <p>生成失败</p>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  if (!imageUrl) {
    return (
      <div className="preview-section">
        <div className="preview-container empty">
          <IconEmpty className="empty-icon" aria-hidden />
          <p>等待生成...</p>
          <span>输入提示词，选择风格，开始创作</span>
        </div>
      </div>
    );
  }

  return (
    <div className="preview-section">
      <div className="preview-container">
        <img src={imageUrl} alt="生成的表情包" className="preview-image" />
        {(provider || isMock) && (
          <div className={`provider-badge ${isMock ? 'mock' : ''}`}>
            {isMock ? 'MOCK' : 'PROVIDER'}: {provider || 'unknown'}
          </div>
        )}
      </div>
      {notice && <div className="preview-notice">{notice}</div>}
    </div>
  );
};

export default PreviewComponent;
