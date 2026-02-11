import React from 'react';
import { IconTrash } from './Icons';

interface HistoryItem {
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

interface HistoryProps {
  history: HistoryItem[];
  onSelect: (item: HistoryItem) => void;
  onDelete: (id: string) => void;
  favoriteIds: string[];
  onToggleFavorite: (id: string) => void;
}

const HistoryComponent: React.FC<HistoryProps> = ({
  history,
  onSelect,
  onDelete,
  favoriteIds,
  onToggleFavorite,
}) => {
  const formatDateTime = (value: string) =>
    new Date(value).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });

  if (history.length === 0) {
    return (
      <div className="history-content empty">
        <p>还没有生成记录</p>
        <span>开始创作你的第一个表情包吧！</span>
      </div>
    );
  }

  return (
    <div className="history-content">
      <h3>生成历史</h3>
      <div className="history-list">
        {history.map((item) => (
          <div key={item.id} className="history-item">
            <button
              type="button"
              className="history-thumb-btn"
              onClick={() => onSelect(item)}
              aria-label={`查看历史记录：${item.prompt}`}
            >
              <img
                src={item.imageUrl}
                alt={item.prompt}
                className="history-thumbnail"
              />
            </button>
            <div className="history-main">
              <div className="history-info">
                <p className="history-prompt">{item.prompt}</p>
                <span className="history-style">{item.style}</span>
                {item.provider && (
                  <span className="history-provider">
                    {item.isMock ? 'MOCK' : 'PROVIDER'}: {item.provider}
                  </span>
                )}
                <span className="history-date">
                  {formatDateTime(item.createdAt)}
                </span>
              </div>
              <div className="history-actions">
                <button
                  type="button"
                  className="history-select"
                  onClick={() => onSelect(item)}
                  aria-label="复用该配置并预览"
                >
                  复用
                </button>
                <button
                  type="button"
                  className={`history-fav ${favoriteIds.includes(item.id) ? 'active' : ''}`}
                  onClick={() => onToggleFavorite(item.id)}
                  aria-label="收藏该条记录"
                >
                  ★
                </button>
                <button
                  type="button"
                  className="history-delete"
                  onClick={() => onDelete(item.id)}
                  aria-label="删除该条记录"
                >
                  <IconTrash className="history-delete-icon" aria-hidden />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistoryComponent;
export type { HistoryItem };
