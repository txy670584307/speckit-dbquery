<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>

<style>
/* ========== 全局基础样式 ========== */
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
               'Helvetica Neue', Arial, 'Noto Sans', 'PingFang SC',
               'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1d2129;
  background: #f2f3f5;
}

/* ========== 滚动条美化 ========== */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background-color: #c9cdd4;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background-color: #86909c;
}

/* ========== 过渡动画 ========== */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

.slide-enter-active, .slide-leave-active {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.slide-enter, .slide-leave-to {
  transform: translateY(-4px);
  opacity: 0;
}

/* ========== Element UI 主题覆盖 ========== */

/* --- 主色 --- */
.el-button--primary {
  background-color: #1677ff;
  border-color: #1677ff;
}
.el-button--primary:hover {
  background-color: #4096ff;
  border-color: #4096ff;
}
.el-button--primary:active {
  background-color: #0958d9;
  border-color: #0958d9;
}
.el-button--primary.is-disabled {
  background-color: #a0cfff;
  border-color: #a0cfff;
}

/* --- 默认按钮 --- */
.el-button--default:hover {
  color: #1677ff;
  border-color: #1677ff;
}

/* --- 文字按钮 --- */
.el-button--text {
  color: #1677ff;
}
.el-button--text:hover {
  color: #4096ff;
}

/* --- 警告按钮 --- */
.el-button--warning {
  background-color: #ff7d00;
  border-color: #ff7d00;
}

/* --- 输入框 --- */
.el-input__inner {
  border-color: #e5e6eb;
  border-radius: 4px;
  height: 32px;
  line-height: 32px;
}
.el-input__inner:focus {
  border-color: #1677ff;
}
.el-input__inner::placeholder {
  color: #86909c;
}

.el-textarea__inner {
  border-color: #e5e6eb;
  border-radius: 4px;
}
.el-textarea__inner:focus {
  border-color: #1677ff;
}
.el-textarea__inner::placeholder {
  color: #86909c;
}

/* --- 表格 --- */
.el-table th.el-table__cell {
  background-color: #f2f3f5;
  color: #1d2129;
  font-weight: 500;
  font-size: 13px;
}
.el-table--small th.el-table__cell {
  padding: 6px 0;
}
.el-table--striped .el-table__body tr.el-table__row--striped td {
  background-color: #fafafa;
}
.el-table__body tr:hover > td {
  background-color: #e6f4ff;
}
.el-table--border td.el-table__cell {
  border-bottom: 1px solid #e5e6eb;
}
.el-table--border {
  border-radius: 4px;
}
.el-table--border:not(.el-table--hidden) {
  border: 1px solid #e5e6eb;
}

/* --- 卡片 --- */
.el-card {
  border: 1px solid #e5e6eb;
  border-radius: 6px;
  background: #ffffff;
  transition: box-shadow 0.2s ease;
}
.el-card__header {
  border-bottom: 1px solid #e5e6eb;
  padding: 12px 16px;
}
.el-card__body {
  padding: 12px 16px;
}

/* --- 对话框 --- */
.el-dialog {
  border-radius: 8px;
}
.el-dialog__header {
  font-weight: 600;
  font-size: 16px;
  padding: 24px 24px 0;
}
.el-dialog__body {
  padding: 20px 24px;
}
.el-dialog__footer {
  padding: 0 24px 24px;
}
.el-overlay {
  background-color: rgba(0, 0, 0, 0.4);
}

/* --- 菜单 --- */
.el-menu {
  border-right: none;
}
.el-menu-item {
  height: 36px;
  line-height: 36px;
  font-size: 13px;
  color: #4e5969;
  border-radius: 4px;
  margin: 2px 4px;
  transition: background-color 0.15s ease;
}
.el-menu-item:hover {
  background-color: #f2f3f5;
}
.el-menu-item.is-active {
  background-color: #e6f4ff;
  color: #1677ff;
  font-weight: 500;
  border-left: 3px solid #1677ff;
  border-radius: 0 4px 4px 0;
  margin-left: 0;
  padding-left: 7px;
}

/* --- 树 --- */
.el-tree {
  background: transparent;
}
.el-tree-node__content {
  height: 32px;
  border-radius: 4px;
}
.el-tree-node__expand-icon {
  color: #86909c;
  font-size: 12px;
}
.el-tree-node__content:hover {
  background-color: #f2f3f5;
}
.el-tree-node:focus > .el-tree-node__content {
  background-color: #e6f4ff;
}

/* --- 标签 --- */
.el-tag--info {
  background-color: #f2f3f5;
  border-color: #e5e6eb;
  color: #86909c;
}
.el-tag--warning {
  background-color: #fff7e6;
  border-color: #ffd591;
  color: #ff7d00;
}
.el-tag--mini {
  border-radius: 2px;
}

/* --- 单选框按钮组 --- */
.el-radio-group.el-radio-group--small .el-radio-button__inner {
  font-size: 13px;
  padding: 6px 16px;
  height: 32px;
  line-height: 20px;
}
.el-radio-button__inner {
  border-color: #e5e6eb;
  color: #4e5969;
}
.el-radio-button__orig-radio:checked + .el-radio-button__inner {
  background-color: #1677ff;
  border-color: #1677ff;
  box-shadow: -1px 0 0 0 #1677ff;
}

/* --- 表单 --- */
.el-form-item__label {
  color: #4e5969;
  font-size: 13px;
}

/* --- 提示消息 --- */
.el-message {
  border-radius: 6px;
  border: 1px solid #e5e6eb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

/* --- 空状态通用样式 --- */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #86909c;
  text-align: center;
}
.empty-state .empty-icon {
  font-size: 36px;
  margin-bottom: 12px;
  color: #c9cdd4;
}
.empty-state .empty-text {
  font-size: 14px;
  line-height: 1.6;
}
.empty-state .empty-hint {
  font-size: 12px;
  color: #c9cdd4;
  margin-top: 8px;
}
</style>
