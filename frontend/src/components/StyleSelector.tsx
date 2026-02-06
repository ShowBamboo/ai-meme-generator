import React from 'react';
import { IconPaint, IconPencil, IconMask, IconCamera, IconFilm, IconDiamond } from './Icons';

type StyleType = 'cartoon' | 'hand-drawn' | 'anime' | 'realistic' | 'retro' | 'minimalist';

interface StyleOption {
  id: StyleType;
  name: string;
  Icon: React.FC<{ className?: string }>;
  description: string;
}

const styleOptions: StyleOption[] = [
  { id: 'cartoon', name: '卡通风格', Icon: IconPaint, description: '夸张的线条和色彩' },
  { id: 'hand-drawn', name: '手绘风格', Icon: IconPencil, description: '随意的手绘线条感' },
  { id: 'anime', name: '动漫风格', Icon: IconMask, description: '日式动漫美学' },
  { id: 'realistic', name: '真人风格', Icon: IconCamera, description: '逼真的人物效果' },
  { id: 'retro', name: '复古风格', Icon: IconFilm, description: '怀旧的像素风' },
  { id: 'minimalist', name: '极简风格', Icon: IconDiamond, description: '简洁的线条设计' },
];

interface StyleSelectorProps {
  selectedStyle: StyleType;
  onStyleChange: (style: StyleType) => void;
  styleStrength: number;
  onStyleStrengthChange: (value: number) => void;
}

const StyleSelector: React.FC<StyleSelectorProps> = ({
  selectedStyle,
  onStyleChange,
  styleStrength,
  onStyleStrengthChange
}) => {
  return (
    <div className="style-selector">
      <h3>选择风格</h3>
      <div className="style-grid">
        {styleOptions.map((style) => (
          <button
            key={style.id}
            type="button"
            className={`style-option ${selectedStyle === style.id ? 'active' : ''}`}
            onClick={() => onStyleChange(style.id)}
            aria-pressed={selectedStyle === style.id}
            aria-label={`选择${style.name}`}
          >
            <span className="style-icon"><style.Icon aria-hidden /></span>
            <span className="style-name">{style.name}</span>
            <span className="style-desc">{style.description}</span>
          </button>
        ))}
      </div>
      <div className="style-strength">
        <div className="style-strength-header">
          <span>风格强度</span>
          <span className="style-strength-value">
            {styleStrength === 1 ? '弱' : styleStrength === 2 ? '中' : '强'}
          </span>
        </div>
        <input
          type="range"
          min={1}
          max={3}
          step={1}
          value={styleStrength}
          onChange={(e) => onStyleStrengthChange(Number(e.target.value))}
          aria-label="风格强度"
        />
      </div>
    </div>
  );
};

export { StyleSelector, styleOptions };
export type { StyleType };
