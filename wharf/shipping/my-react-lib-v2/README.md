# my-react-lib 🌱

> React 组件库，专为 Next.js 16 + Ant Design 5 设计

## 📦 安装

### 通过 Git 安装（推荐开发阶段）

```bash
# npm
npm install git+https://github.com/yourname/my-react-lib.git#v1.0.0

# yarn
yarn add git+https://github.com/yourname/my-react-lib.git#v1.0.0

# pnpm
pnpm add git+https://github.com/yourname/my-react-lib.git#v1.0.0
```

> 🔖 建议指定 tag/commit 保证版本稳定：`#v1.0.0` 或 `#abc1234`

### 通过 npm 安装（发布后）

```bash
npm install my-react-lib
```

## 🚀 使用

```tsx
'use client';

import { Button, ScallionButton } from 'my-react-lib';

export default function Page() {
  return (
    <div>
      <Button type="primary">普通按钮</Button>
      <ScallionButton withScallion>带葱花的按钮 🌱</ScallionButton>
    </div>
  );
}
```

## ⚙️ 依赖要求

确保你的项目已安装以下 peer dependencies：

```json
{
  "react": "^18.3.1",
  "react-dom": "^18.3.1", 
  "next": "^16.1.3",
  "antd": "^5.x"
}
```

## 🛠️ 开发

```bash
# 安装依赖
pnpm install

# 开发模式（监听构建）
pnpm dev

# 生产构建
pnpm build

# 类型检查
pnpm typecheck
```

## 📄 License

MIT