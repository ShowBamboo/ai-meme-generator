import React, { useEffect, useState } from 'react';
import { IconDownload, IconCopy, IconCheck, IconSparkle, IconDiamond } from './Icons';

interface DownloadProps {
  imageUrl: string;
  onShare?: (platform: string) => void;
  upscaledImageUrl?: string | null;
  onUpscale?: () => void;
  upscaling?: boolean;
  upscaleError?: string;
}

const DownloadComponent: React.FC<DownloadProps> = ({
  imageUrl,
  upscaledImageUrl,
  onUpscale,
  upscaling,
  upscaleError,
}) => {
  const [copied, setCopied] = useState(false);
  const [compareOpen, setCompareOpen] = useState(false);
  const [activeCompare, setActiveCompare] = useState<'origin' | 'upscaled'>('upscaled');
  const [origSize, setOrigSize] = useState<string>('');
  const [upSize, setUpSize] = useState<string>('');

  useEffect(() => {
    const img = new Image();
    img.onload = () => setOrigSize(`${img.naturalWidth}×${img.naturalHeight}`);
    img.src = imageUrl;
  }, [imageUrl]);

  useEffect(() => {
    if (!upscaledImageUrl) return;
    const img = new Image();
    img.onload = () => setUpSize(`${img.naturalWidth}×${img.naturalHeight}`);
    img.src = upscaledImageUrl;
  }, [upscaledImageUrl]);

  useEffect(() => {
    if (upscaledImageUrl) {
      setCompareOpen(true);
      setActiveCompare('upscaled');
    }
  }, [upscaledImageUrl]);

  const handleDownload = async (urlToDownload: string) => {
    try {
      const response = await fetch(urlToDownload);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `meme-${Date.now()}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('下载失败:', error);
    }
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(upscaledImageUrl || imageUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('复制失败:', error);
    }
  };

  const handleShare = (platform: string) => {
    const text = encodeURIComponent('看看我生成的 AI 表情包！');
    const currentUrl = encodeURIComponent(upscaledImageUrl || imageUrl);
    let shareUrl = '';

    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${text}&url=${currentUrl}`;
        break;
      case 'weibo':
        shareUrl = `https://service.weibo.com/share/share.php?url=${currentUrl}&title=${text}`;
        break;
    }

    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
    }
  };

  return (
    <div className="download-section">
      <button type="button" className="download-btn primary" onClick={() => handleDownload(imageUrl)} aria-label="下载图片">
        <IconDownload className="btn-icon" aria-hidden /> 下载图片
      </button>
      <button
        type="button"
        className="download-btn premium"
        onClick={onUpscale}
        disabled={upscaling || !onUpscale}
        aria-label="超清增强"
      >
        <IconSparkle className="btn-icon" aria-hidden /> {upscaling ? '超清处理中...' : '超清增强'}
      </button>
      {upscaledImageUrl && (
        <button
          type="button"
          className="download-btn secondary"
          onClick={() => handleDownload(upscaledImageUrl)}
          aria-label="下载超清"
        >
          <IconDiamond className="btn-icon" aria-hidden /> 下载超清
        </button>
      )}
      <button type="button" className="download-btn secondary" onClick={handleCopyLink} aria-label={copied ? '已复制' : '复制链接'}>
        {copied ? <IconCheck className="btn-icon" aria-hidden /> : <IconCopy className="btn-icon" aria-hidden />}
        {copied ? '已复制!' : '复制链接'}
      </button>
      <div className="share-buttons">
        <button type="button" className="share-btn twitter" onClick={() => handleShare('twitter')} aria-label="分享到 Twitter">
          Twitter
        </button>
        <button type="button" className="share-btn weibo" onClick={() => handleShare('weibo')} aria-label="分享到微博">
          微博
        </button>
      </div>
      {upscaleError && <p className="upscale-error">{upscaleError}</p>}

      {upscaledImageUrl && (
        <div className="compare-section">
          <div className="compare-header">
            <h4>超清对比</h4>
            <button
              type="button"
              className="compare-toggle"
              onClick={() => setCompareOpen((prev) => !prev)}
            >
              {compareOpen ? '收起' : '展开'}
            </button>
          </div>
          {compareOpen && (
            <>
              <div className="compare-grid">
                <button
                  type="button"
                  className={`compare-pane ${activeCompare === 'origin' ? 'active' : ''}`}
                  onClick={() => setActiveCompare('origin')}
                >
                  <span className="compare-tag">原图 {origSize || '-'}</span>
                  <img
                    src={imageUrl}
                    alt="原图"
                    className="compare-img"
                  />
                </button>
                <button
                  type="button"
                  className={`compare-pane ${activeCompare === 'upscaled' ? 'active' : ''}`}
                  onClick={() => setActiveCompare('upscaled')}
                >
                  <span className="compare-tag">超清 {upSize || '-'}</span>
                  <img
                    src={upscaledImageUrl}
                    alt="超清图"
                    className="compare-img"
                  />
                </button>
              </div>
              <div className="compare-focus">
                <span className="compare-focus-label">
                  当前查看：{activeCompare === 'upscaled' ? '超清图' : '原图'}
                </span>
                <img
                  src={activeCompare === 'upscaled' ? upscaledImageUrl : imageUrl}
                  alt={activeCompare === 'upscaled' ? '超清图预览' : '原图预览'}
                  className="compare-focus-image"
                />
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default DownloadComponent;
