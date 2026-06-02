<template>
  <div class="sql-editor-wrapper" style="height: 100%; display: flex; flex-direction: column;">
    <!-- 工具栏 -->
    <div class="editor-toolbar">
      <div style="display: flex; align-items: center; gap: 8px;">
        <i class="el-icon-s-unfold" style="color: #86909c; font-size: 14px;"></i>
        <span style="font-size: 12px; color: #86909c;">
          按 <kbd class="key-hint">Ctrl</kbd>+<kbd class="key-hint">Enter</kbd> 执行
        </span>
      </div>
      <el-button type="primary" size="small" :loading="executing" @click="execute">
        <i class="el-icon-video-play" style="margin-right: 4px;"></i> 执行
      </el-button>
    </div>
    <!-- Monaco Editor 容器 -->
    <div ref="editorContainer" style="flex: 1; min-height: 200px;"></div>
  </div>
</template>

<script>
import * as monaco from 'monaco-editor';

export default {
  name: 'SqlEditor',
  props: {
    value: { type: String, default: '' },
    executing: { type: Boolean, default: false },
  },
  data() {
    return { editor: null };
  },
  mounted() {
    this.editor = monaco.editor.create(this.$refs.editorContainer, {
      value: this.value || '',
      language: 'sql',
      theme: 'vs',
      minimap: { enabled: false },
      automaticLayout: true,
      fontSize: 14,
      lineNumbers: 'on',
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      padding: { top: 8 },
      renderLineHighlight: 'line',
    });

    this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      this.execute();
    });

    this.editor.onDidChangeModelContent(() => {
      this.$emit('input', this.editor.getValue());
    });
  },
  beforeDestroy() {
    if (this.editor) {
      this.editor.dispose();
    }
  },
  methods: {
    execute() {
      this.$emit('execute');
    },
    setValue(sql) {
      if (this.editor) {
        this.editor.setValue(sql);
      }
    },
    focus() {
      if (this.editor) {
        this.editor.focus();
      }
    },
  },
};
</script>

<style scoped>
.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #e5e6eb;
  background: #fafafa;
}
.key-hint {
  border: 1px solid #e5e6eb;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 11px;
  background: #ffffff;
  font-family: inherit;
}
</style>
