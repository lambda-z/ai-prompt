

## 组件名：ScallionTab


## 输入：
- tabItems: 
  - title: string
    icon: url
    content: ReactNode
- onTabChange: (index: number) => void
- height: number | string
- width: number | string
- centerTabSize: number (default: 1) - 中间标签占比，范围0-1

### 参数解释：
- `tabItems`: 标签页项列表，每项包含标签文本、图标URL和内容组件。
- `onTabChange`: 标签切换回调函数，接收当前标签索引作为参数。
- `height`: 组件高度，可以是数字（像素）或字符串（如'100%'）。
- `width`: 组件宽度，可以是数字（像素）或字符串（如'100%'）。
- `centerTabSize`: 中间标签占比，默认为1，范围0-1，控制中间标签的宽度占比

## 输出：ReactNode
