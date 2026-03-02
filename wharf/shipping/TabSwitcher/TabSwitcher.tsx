import React, { useState } from 'react';
import { TabItem } from './types';
import './TabSwitcher.css';

/**
 * @component TabSwitcher
 * @description 时尚现代的 Tab 切换组件，支持渐变风格和图标
 * @param {TabItem[]} tabItems - 标签页数据数组
 * 
 * @example
 * <TabSwitcher tabItems={[
 *  { title: 'Home', icon: <HomeIcon />, content: <HomeContent /> }
 * ]} />
 */
const TabSwitcher: React.FC<{ tabItems: TabItem[] }> = ({ tabItems }) => {
  // 状态管理：当前激活的索引
  const [activeIndex, setActiveIndex] = useState<number>(0);

  // 边界检查：确保至少有一个 tab
  if (!tabItems || tabItems.length === 0) {
    return <div className="tab-switcher-container">No tabs provided</div>;
  }

  // 处理点击事件
  const handleTabClick = (index: number) => {
    setActiveIndex(index);
  };

  return (
    <div className="tab-switcher-container">
      {/* 标签列表 */}
      <div className="tab-list" role="tablist">
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
            {/* 图标区域 */}
            <span className="tab-item-icon">{item.icon}</span>
            {/* 标题区域 */}
            <span>{item.title}</span>
          </div>
        ))}
      </div>

      {/* 内容显示区域 */}
      <div className="tab-content-wrapper" role="tabpanel">
        {tabItems[activeIndex].content}
      </div>
    </div>
  );
};

export default TabSwitcher;
