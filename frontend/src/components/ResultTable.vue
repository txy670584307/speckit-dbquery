<template>
  <div class="result-table" style="height: 100%; display: flex; flex-direction: column;">
    <!-- 标头信息 -->
    <div v-if="result" class="result-header">
      <span>
        查询结果：<strong>{{ result.rowCount }}</strong> 行
        <el-tag v-if="result.truncated" type="warning" size="mini" style="margin-left: 6px;">
          已限制显示前 1000 行
        </el-tag>
      </span>
      <span class="result-sql" :title="result.sqlExecuted">SQL: {{ result.sqlExecuted }}</span>
    </div>

    <!-- 空结果 -->
    <div v-if="result && result.rowCount === 0" class="empty-state" style="flex: 1;">
      <div style="font-size: 32px; margin-bottom: 8px;">📭</div>
      <div class="empty-text">查询未返回任何结果</div>
    </div>

    <!-- 数据表格 -->
    <div v-else-if="result && result.columns.length > 0" style="flex: 1; overflow: auto;">
      <el-table
        :data="tableData"
        border
        stripe
        size="small"
        :max-height="tableMaxHeight"
        style="width: 100%;"
      >
        <el-table-column
          v-for="col in result.columns"
          :key="col.name"
          :prop="col.name"
          :label="col.name"
          min-width="120"
          show-overflow-tooltip
        >
          <template slot-scope="{ row }">
            <span v-if="row[col.name] === null" style="color: #c9cdd4; font-style: italic;">NULL</span>
            <span v-else-if="typeof row[col.name] === 'boolean'">
              <el-tag :type="row[col.name] ? 'success' : 'info'" size="mini">
                {{ row[col.name] ? 'true' : 'false' }}
              </el-tag>
            </span>
            <span v-else>{{ row[col.name] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 无结果 -->
    <div v-if="!result" class="empty-state" style="flex: 1;">
      <div class="empty-icon">🔍</div>
      <div class="empty-text">执行查询后结果将在此显示</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ResultTable',
  props: {
    result: { type: Object, default: null },
  },
  data() {
    return { tableMaxHeight: 500 };
  },
  computed: {
    tableData() {
      if (!this.result || !this.result.rows) return [];
      const columns = this.result.columns;
      return this.result.rows.map(row => {
        const obj = {};
        columns.forEach((col, i) => {
          obj[col.name] = row[i];
        });
        return obj;
      });
    },
  },
  mounted() {
    this.calculateHeight();
    window.addEventListener('resize', this.calculateHeight);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.calculateHeight);
  },
  methods: {
    calculateHeight() {
      const el = this.$el?.parentElement;
      if (el) {
        this.tableMaxHeight = el.clientHeight - 60;
      }
    },
  },
};
</script>

<style scoped>
.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid #e5e6eb;
  background: #fafafa;
  font-size: 12px;
}
.result-sql {
  color: #86909c;
  font-size: 11px;
  max-width: 60%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
