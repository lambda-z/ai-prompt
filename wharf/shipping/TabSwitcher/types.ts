import React from 'react';

/**
 * @interface TabItem
 * @description 定义 Tab 切换组件的数据结构
 * @property title - 标签页标题
 * @property icon - 标签页图标，支持 React 节点
 * @property content - 标签页内容，支持 React 节点
 */
export interface TabItem {
  title: string;
  icon: React.ReactNode;
  content: React.ReactNode;
}
