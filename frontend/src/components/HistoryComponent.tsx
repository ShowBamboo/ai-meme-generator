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
  if (history.length === 0) {
    return (
      <div className="history-section empty">
        <p>还没有生成记录</p>
        <span>开始创作你的第一个表情包吧！</span>
      </div>
    );
  }

  return (
    <div className="history-section">
      <h3>生成历史</h3>
      <div className="history-list">
        {history.map((item) => (
          <div key={item.id} className="history-item">
            <img
              src={item.imageUrl}
              alt={item.prompt}
              className="history-thumbnail"
              onClick={() => onSelect(item)}
            />
            <div className="history-info">
              <p className="history-prompt">{item.prompt}</p>
              <span className="history-style">{item.style}</span>
              {item.provider && (
                <span className="history-provider">
                  {item.isMock ? 'MOCK' : 'PROVIDER'}: {item.provider}
                </span>
              )}
              <span className="history-date">
                {new Date(item.createdAt).toLocaleDateString()}
              </span>
            </div>
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
        ))}
      </div>
    </div>
  );
};

export default HistoryComponent;
export type { HistoryItem };
