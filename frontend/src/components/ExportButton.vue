<template>
  <div class="export-button" style="display: inline-flex; align-items: center; gap: 6px;">
    <el-dropdown
      v-if="hasResult"
      trigger="click"
      @command="handleExport"
    >
      <el-button size="mini" type="primary" icon="el-icon-download" :loading="exporting">
        导出 <i class="el-icon-arrow-down el-icon--right" />
      </el-button>
      <el-dropdown-menu slot="dropdown">
        <el-dropdown-item command="csv">
          <i class="el-icon-document" style="margin-right: 6px;" />导出为 CSV
        </el-dropdown-item>
        <el-dropdown-item command="json">
          <i class="el-icon-document" style="margin-right: 6px;" />导出为 JSON
        </el-dropdown-item>
      </el-dropdown-menu>
    </el-dropdown>

    <!-- 导出提示横幅（AI 主动提示） -->
    <transition name="fade">
      <span v-if="showPrompt && hasResult" class="export-prompt">
        <i class="el-icon-info" style="margin-right: 4px; color: #1677ff;"></i>
        需要将这次查询结果导出为 CSV 或 JSON 文件吗？
        <el-button type="text" size="mini" style="margin-left: 4px;" @click="handleExport('csv')">CSV</el-button>
        <el-button type="text" size="mini" @click="handleExport('json')">JSON</el-button>
        <el-button type="text" size="mini" style="color: #86909c;" @click="dismissPrompt">忽略</el-button>
      </span>
    </transition>
  </div>
</template>

<script>
import { exportQuery } from '../services/api';

export default {
  name: 'ExportButton',
  props: {
    dbName: { type: String, required: true },
    sql: { type: String, default: '' },
    hasResult: { type: Boolean, default: false },
    showPrompt: { type: Boolean, default: false },
  },
  data() {
    return { exporting: false };
  },
  methods: {
    async handleExport(format) {
      if (!this.sql.trim()) {
        this.$message.warning('没有可导出的 SQL 语句');
        return;
      }
      this.exporting = true;
      try {
        const { blob, filename } = await exportQuery(this.dbName, this.sql, format);
        this.downloadBlob(blob, filename);
        this.$message.success(`已导出为 ${format.toUpperCase()} 文件`);
        this.$emit('exported');
      } catch (e) {
        // 尝试从 Blob 错误中提取错误信息
        try {
          const text = await e.response?.data?.text?.();
          if (text) {
            const err = JSON.parse(text);
            this.$message.error(err.detail?.message || '导出失败');
            return;
          }
        } catch (_) { /* ignore parse errors */ }
        this.$message.error(e.message || '导出失败');
      } finally {
        this.exporting = false;
      }
    },
    downloadBlob(blob, filename) {
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    },
    dismissPrompt() {
      this.$emit('dismiss-prompt');
    },
  },
};
</script>

<style scoped>
.export-prompt {
  font-size: 12px;
  color: #4e5969;
  background: #e6f4ff;
  border: 1px solid #91caff;
  border-radius: 4px;
  padding: 4px 10px;
  display: inline-flex;
  align-items: center;
  white-space: nowrap;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
