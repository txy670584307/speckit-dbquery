# 前端样式规范

> 参考自 TRAE Solo (trae.cn/solo-web) 设计语言
> 适用于 Vue 2 + Element UI 项目

---

## 一、设计原则

| 原则 | 说明 |
|------|------|
| **简洁清晰** | 去除冗余装饰，信息层级分明 |
| **留白充裕** | 区块之间保持充足间距，呼吸感 |
| **信息优先** | 内容是最重要的视觉元素，UI 服务于内容 |
| **一致性** | 颜色、间距、字体、组件风格全站统一 |

---

## 二、色彩体系

### 2.1 主色调

| 用途 | 色值 | 说明 |
|------|------|------|
| 品牌色 / Primary | `#1677ff` | 按钮、链接、选中状态、焦点边框 |
| Primary Hover | `#4096ff` | 按钮 hover |
| Primary Active | `#0958d9` | 按钮 active / pressed |
| Primary Background | `#e6f4ff` | 浅色背景、标签、提示条 |

### 2.2 中性色

| 用途 | 色值 | 说明 |
|------|------|------|
| 正文文字 | `#1d2129` | 主要标题和正文 |
| 次要文字 | `#4e5969` | 次要信息、描述文字 |
| 辅助文字 | `#86909c` | 占位符、辅助提示 |
| 禁用文字 | `#c9cdd4` | 禁用状态 |
| 分割线 | `#e5e6eb` | 边框、分割线 |
| 背景灰 | `#f2f3f5` | 页面背景、卡片背景 |
| 纯白 | `#ffffff` | 卡片背景、弹窗背景 |

### 2.3 语义色

| 用途 | 色值 | 说明 |
|------|------|------|
| 成功 | `#00b42a` | 成功提示、通过状态 |
| 警告 | `#ff7d00` | 警告提示、LIMIT 截断标签 |
| 错误 | `#f53f3f` | 错误提示、删除操作 |
| 链接 | `#1677ff` | 可点击链接 |

---

## 三、字体与排版

### 3.1 字体栈

```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC',
             'Microsoft YaHei', sans-serif;
```

### 3.2 字号层级

| 层级 | 字号 | 行高 | 字重 | 用途 |
|------|------|------|------|------|
| Hero Title | 24px | 1.4 | 600 | 页面大标题 |
| Section Title | 18px | 1.5 | 600 | 区块标题 |
| Card Title | 16px | 1.5 | 500 | 卡片标题 |
| Body | 14px | 1.6 | 400 | 正文 |
| Secondary | 13px | 1.5 | 400 | 次要信息 |
| Small | 12px | 1.5 | 400 | 辅助文字、标签 |
| Mini | 11px | 1.4 | 400 | 极小提示 |

### 3.3 行高规范

- 标题类：`line-height: 1.4 ~ 1.5`
- 正文类：`line-height: 1.6`
- 紧凑型（表格、列表）：`line-height: 1.4`

---

## 四、间距体系

采用 4px 为基准单位（4px × n）。

| 间距层级 | 值 | 用途 |
|---------|-----|------|
| 2x | 8px | 紧凑间距、图标与文字间距 |
| 3x | 12px | 卡片内边距、表单标签间距 |
| 4x | 16px | 标准间距、区块内间距 |
| 6x | 24px | 区块间距、卡片间距 |
| 8x | 32px | 大区块间距 |
| 10x | 40px | 页面边距、大段间距 |

---

## 五、布局规范

### 5.1 页面布局

```
┌─────────────────────────────────────────────────┐
│  导航栏 (48px ~ 56px)                           │
├─────────┬───────────────────────────────────────┤
│         │                                       │
│ 侧边栏   │  内容主区域                           │
│ 280~320px│                                       │
│         │                                       │
│         │                                       │
└─────────┴───────────────────────────────────────┘
```

- **导航栏高度**: 48px ~ 56px，固定顶部
- **侧边栏宽度**: 280px ~ 320px，带右侧 1px 分割线
- **内容区域**: 自适应剩余宽度，内边距 16px~24px
- **页面最小宽度**: 1024px

### 5.2 左右分栏

```
┌──────────────┬──────────────────────────────────┐
│  面板标题     │  操作按钮区                       │
│  font-weight: 600                               │
├──────────────┤──────────────────────────────────┤
│  内容列表     │  详情 / 编辑器 / 结果             │
│              │                                  │
└──────────────┴──────────────────────────────────┘
```

- 左侧面板标题：14px, 600 weight
- 区块间用 `border-bottom: 1px solid #e5e6eb` 分隔
- 面板头部 flex 布局：标题居左、操作用 `margin-left: auto` 靠右

---

## 六、组件样式

### 6.1 卡片 (Card)

| 属性 | 值 |
|------|----|
| border-radius | 6px |
| box-shadow | `0 1px 3px rgba(0,0,0,0.06)` (或 `none` 极简) |
| 内边距 | 16px |
| 头部 | 14px semibold + 操作按钮 |
| 背景 | `#ffffff` |

### 6.2 按钮 (Button)

| 类型 | 样式 |
|------|------|
| Primary | 背景 `#1677ff`，白色文字，hover `#4096ff` |
| Default | 白色背景，`#4e5969` 文字，hover 边框变 primary |
| Text | 无边框，纯文字，hover 变 primary |
| Mini / Small | 字号 12px，内边距紧凑 |

### 6.3 输入框 (Input / Textarea)

| 属性 | 值 |
|------|----|
| 高度 | 32px (默认) / 28px (small) |
| 边框色 | `#e5e6eb` -> focus `#1677ff` |
| 圆角 | 4px |
| placeholder | `#86909c` |

### 6.4 表格 (Table)

| 属性 | 值 |
|------|----|
| 表头背景 | `#f2f3f5` |
| 表头文字 | 13px, 500 weight, `#1d2129` |
| 表行 | 交替色 `#fafafa` (stripe) |
| 行高 | 36px (small) |
| 边框 | `1px solid #e5e6eb` |
| 圆角 | 4px |

### 6.5 树形控件 (Tree)

| 属性 | 值 |
|------|----|
| 节点高度 | 32px |
| 缩进 | 20px |
| 展开图标 | 12px, `#86909c` |
| hover 背景 | `#f2f3f5` |
| 选中背景 | `#e6f4ff` |

### 6.6 标签 (Tag)

| 类型 | 样式 |
|------|------|
| info | 浅灰背景，灰色文字（如 `nullable`） |
| warning | 浅黄背景 `#fff7e6`，橙色文字（如截断提示） |
| 圆角 | 2px，小号 |

### 6.7 对话框 (Dialog / Modal)

| 属性 | 值 |
|------|----|
| 宽度 | 480px (默认) / 640px (大) |
| 圆角 | 8px |
| 遮罩 | `rgba(0,0,0,0.4)` |
| 头部 | 16px, 600 weight |
| 内边距 | 24px |
| 底部操作栏 | 8px 间距，右对齐 |

---

## 七、Element UI 覆盖

全局覆盖 Element UI 默认样式（在 `App.vue` 或独立 CSS 文件中）：

```css
/* 主色覆盖 */
.el-button--primary {
  background-color: #1677ff;
  border-color: #1677ff;
}
.el-button--primary:hover {
  background-color: #4096ff;
  border-color: #4096ff;
}

/* 输入框聚焦 */
.el-input__inner:focus,
.el-textarea__inner:focus {
  border-color: #1677ff;
}

/* 表格表头 */
.el-table th.el-table__cell {
  background-color: #f2f3f5;
  color: #1d2129;
  font-weight: 500;
}

/* 卡片 */
.el-card {
  border: 1px solid #e5e6eb;
  border-radius: 6px;
}

/* 对话框 */
.el-dialog {
  border-radius: 8px;
}
.el-dialog__header {
  font-weight: 600;
  font-size: 16px;
}

/* 菜单选中色 */
.el-menu-item.is-active {
  background-color: #e6f4ff;
  color: #1677ff;
  border-right: 3px solid #1677ff;
}

/* 树节点展开图标 */
.el-tree-node__expand-icon {
  color: #86909c;
}
```

---

## 八、设计示例对照

### TRAE Solo 风格 → 本项目映射

| TRAE 元素 | 本项目对应 | 样式要点 |
|-----------|-----------|---------|
| 导航栏 "产品 企业版 价格..." | 顶部模式切换 (SQL / 自然语言) | 48px 高，`#fafafa` 背景，15px 字号 |
| 功能卡片网格 | 表/视图树卡片 | 无阴影，14px 标题，12px 内边距 |
| Hero 大标题 | 页面空状态提示 | 16px, 600 weight, 居中, 灰色 |
| 操作按钮 CTA | "添加"、"执行"、"生成 SQL" | Primary 蓝色，small 尺寸 |
| 列表项 | 数据库连接列表 | el-menu-item, 36px 高, 选中蓝色指示条 |
| 分割线 | 左右面板分隔 | 1px solid `#e5e6eb` |

---

## 九、检查清单

开发前端组件时对照检查：

- [ ] 色彩是否使用规范色值（非随意取色）
- [ ] 间距是否符合 4px 基准体系
- [ ] 字号是否匹配层级规范
- [ ] 卡片是否使用 6px 圆角
- [ ] 按钮类型选择是否正确（Primary / Default / Text）
- [ ] 空状态 / 加载态 / 错误态是否都有对应 UI
- [ ] 表格是否启用 stripe 和 border
- [ ] 弹窗遮罩是否半透明黑色
- [ ] 提示文案风格是否简洁一致
