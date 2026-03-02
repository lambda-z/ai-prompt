import React from 'react';

export interface TabItem {
  title: string;
  icon: React.ReactNode;
  content: React.ReactNode;
}

export interface TabSwitcherProps {
  tabItems: TabItem[];
}
