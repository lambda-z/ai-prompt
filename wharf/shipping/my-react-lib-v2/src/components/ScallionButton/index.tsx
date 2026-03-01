'use client';

import React from 'react';
import { Button } from 'antd';
import styles from './index.module.css';

export interface ScallionButtonProps 
  extends Omit<React.ComponentProps<typeof Button>, 'icon'> {
  withScallion?: boolean;
}

export const ScallionButton: React.FC<ScallionButtonProps> = ({
  withScallion = false,
  children,
  ...props
}) => {
  return (
    <Button {...props}>
      {withScallion && <span className={styles.scallion}>🌱</span>}
      {children}
    </Button>
  );
};

ScallionButton.displayName = 'ScallionButton';