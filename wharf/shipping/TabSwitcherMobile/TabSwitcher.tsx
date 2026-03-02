import React, { useState } from 'react';
import { TabSwitcherProps } from './types';
import './TabSwitcher.css';

/**
 * TabSwitcher Component
 * 
 * Features:
 * - Modern gradient style
 * - Content displayed above tabs (Requirement 10)
 * - Active state changes color, size for both icon and title
 * - Accessible keyboard navigation
 */
export const TabSwitcher: React.FC<TabSwitcherProps> = ({ tabItems }) => {
  // Default first tab is active (Requirement 1)
  const [activeIndex, setActiveIndex] = useState<number>(0);

  if (!tabItems || tabItems.length === 0) {
    return null;
  }

  const handleTabClick = (index: number) => {
    setActiveIndex(index);
  };

  return (
    <div className="tab-switcher-container">
      {/* Content located above tab configuration (Requirement 10) */}
      <div className="content-area">
        {tabItems[activeIndex].content}
      </div>

      {/* Tab Configuration */}
      <div className="tabs-list">
        {tabItems.map((item, index) => (
          <div
            key={index}
            className={`tab-item ${index === activeIndex ? 'active' : ''}`}
            onClick={() => handleTabClick(index)}
            role="tab"
            aria-selected={index === activeIndex}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                handleTabClick(index);
              }
            }}
          >
            {/* Icon above title (Requirement 3) */}
            <div className="tab-icon">{item.icon}</div>
            {/* Title below icon (Requirement 4) */}
            <div className="tab-title">{item.title}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
