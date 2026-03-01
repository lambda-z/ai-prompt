'use client';

import React from 'react';
import { Button as AntdButton, type ButtonProps as AntdButtonProps } from 'antd';
import styles from './index.module.css';

export interface ButtonProps extends AntdButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  className = '',
  ...props
}) => {
  return (
    <AntdButton
      className={`${styles.button} ${styles[variant]} ${className}`}
      {...props}
    />
  );
};

Button.displayName = 'Button';