<template>
  <el-container style="height: 100vh;">
    <!-- ====== 侧边栏：数据库 Token 列表 ====== -->
    <el-aside width="240px" class="sidebar">
      <!-- 侧边栏头部 -->
      <div class="sidebar-header">
        <span class="sidebar-title">数据库</span>
        <el-button type="primary" size="mini" circle icon="el-icon-plus" @click="showAddDialog = true" title="添加数据库连接" />
      </div>

      <!-- Token 列表 -->
      <div class="token-list">
        <div v-if="loadingDbs" class="empty-state" style="padding: 32px 12px;">
          <i class="el-icon-loading"></i>
          <div class="empty-text" style="font-size: 13px; margin-top: 8px;">加载中...</div>
        </div>
        <div v-else-if="dbs.length === 0" class="empty-state" style="padding: 32px 12px;">
          <div class="empty-icon" style="font-size: 24px;">📦</div>
          <div class="empty-text" style="font-size: 13px;">暂无连接</div>
        </div>

        <div
          v-for="db in dbs"
          :key="db.dbName"
          class="db-token"
          :class="{ 'db-token-active': db.dbName === activeDb }"
          @click="onDbSelect(db.dbName)"
        >
          <div class="token-indicator"></div>
          <div class="token-content">
            <div class="token-name">
              <i class="el-icon-document" style="margin-right: 6px; color: #1677ff;"></i>
              {{ db.dbName }}
            </div>
            <div class="token-meta">
              <span class="token-count">{{ db.tableCount }} 个表</span>
              <el-button
                v-if="db.dbName === activeDb"
                type="text"
                size="mini"
                class="token-delete"
                icon="el-icon-close"
                @click.stop="confirmDelete(db.dbName)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 侧边栏底部提示 -->
      <div v-if="dbs.length > 0" class="sidebar-footer">
        <span style="font-size: 11px; color: #c9cdd4;">共 {{ dbs.length }} 个连接</span>
      </div>
    </el-aside>

    <!-- ====== 主内容区域 ====== -->
    <el-main class="main-content">
      <!-- 未选择数据库 -->
      <div v-if="!activeDb" class="empty-state" style="flex: 1;">
        <div class="empty-icon">📊</div>
        <div class="empty-text" style="font-size: 16px;">请添加一个数据库连接</div>
        <div class="empty-hint">点击左侧「+」开始</div>
      </div>

      <template v-else>
        <!-- ---- 数据库信息栏 ---- -->
        <div class="db-info-bar">
          <div class="db-info-left">
            <h2 class="db-info-title">{{ activeDb }}</h2>
            <el-tag size="mini" type="info" style="margin-left: 8px;">{{ metadata.length }} 个表/视图</el-tag>
          </div>
          <div class="db-info-right">
            <el-button size="mini" icon="el-icon-refresh" :loading="refreshingMetadata" @click="refreshMetadata">
              刷新 metadata
            </el-button>
            <el-button size="mini" icon="el-icon-delete" type="danger" plain @click="confirmDelete(activeDb)">
              删除连接
            </el-button>
          </div>
        </div>

        <!-- ---- Metadata 区域（表/视图标签） ---- -->
        <div class="metadata-section">
          <div v-if="loadingMetadata" class="empty-state" style="padding: 16px;">
            <i class="el-icon-loading"></i> 加载中...
          </div>
          <template v-else-if="metadata.length === 0">
            <div class="section-label">表与视图</div>
            <div class="empty-state" style="padding: 12px 0;">
              <span class="empty-text" style="font-size: 13px;">该数据库中没有表或视图</span>
            </div>
          </template>
          <template v-else>
            <div class="section-label">表与视图</div>
            <div class="table-tabs">
              <div
                v-for="tbl in metadata"
                :key="tbl.tableName"
                class="table-tab"
                :class="{ 'table-tab-active': expandedTable === tbl.tableName }"
                @click="toggleTable(tbl.tableName)"
              >
                <i :class="tbl.tableType === 'view' ? 'el-icon-view' : 'el-icon-document'" 
                   :style="{ color: tbl.tableType === 'view' ? '#ff7d00' : '#1677ff' }"></i>
                <span>{{ tbl.tableName }}</span>
                <el-tag size="mini" :type="tbl.tableType === 'view' ? 'warning' : 'primary'" style="margin-left: 4px;">
                  {{ tbl.tableType === 'view' ? '视图' : '表' }}
                </el-tag>
                <i class="el-icon-arrow-down" style="margin-left: 4px; font-size: 12px; color: #86909c; transition: transform 0.2s;"
                   :style="{ transform: expandedTable === tbl.tableName ? 'rotate(0deg)' : 'rotate(-90deg)' }"></i>
              </div>
            </div>
            <!-- 展开的列信息 -->
            <transition name="slide">
              <div v-if="expandedTable" class="columns-panel">
                <div class="columns-header">列信息</div>
                <table class="columns-table">
                  <thead>
                    <tr>
                      <th>列名</th>
                      <th>数据类型</th>
                      <th>可空</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="col in expandedColumns" :key="col.name">
                      <td><code>{{ col.name }}</code></td>
                      <td><span class="type-badge">{{ col.dataType }}</span></td>
                      <td>
                        <el-tag v-if="col.nullable" size="mini" type="info">nullable</el-tag>
                        <span v-else style="color: #c9cdd4;">NOT NULL</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </transition>
          </template>
        </div>

        <!-- ---- 查询区域 ---- -->
        <div class="query-section">
          <!-- 模式切换 -->
          <div class="query-mode-bar">
            <el-radio-group v-model="queryMode" size="small">
              <el-radio-button label="sql">
                <i class="el-icon-edit"></i> SQL 编辑
              </el-radio-button>
              <el-radio-button label="nl">
                <i class="el-icon-chat-dot-round"></i> 自然语言
              </el-radio-button>
            </el-radio-group>
          </div>

          <!-- SQL 模式 -->
          <div v-if="queryMode === 'sql'" class="query-panel-split">
            <div class="editor-pane">
              <SqlEditor v-model="currentSql" :executing="executing" @execute="handleQuery" />
            </div>
            <div class="result-pane">
              <div class="result-toolbar" v-if="queryResult">
                <ExportButton
                  :db-name="activeDb"
                  :sql="currentSql"
                  :has-result="!!queryResult"
                  :show-prompt="showExportPrompt && queryMode === 'sql'"
                  @exported="onExported"
                  @dismiss-prompt="dismissExportPrompt"
                />
              </div>
              <ResultTable :result="queryResult" />
            </div>
          </div>

          <!-- 自然语言模式 -->
          <div v-if="queryMode === 'nl'" class="query-panel-nl">
            <div class="nl-input-area">
              <el-input v-model="naturalText" type="textarea" :rows="4"
                placeholder="用自然语言描述查询需求，如：查询 users 表中所有活跃用户" />
              <el-button type="primary" :loading="executing" @click="handleNaturalQuery" style="margin-top: 8px;">
                <i class="el-icon-ai" style="margin-right: 4px;"></i> 生成 SQL 并查询
              </el-button>
            </div>
            <transition name="slide">
              <div v-if="generatedSql" class="sql-fix-panel">
                <div class="sql-fix-header"><i class="el-icon-warning"></i> 生成的 SQL 无法自动执行，请手动修正</div>
                <el-input v-model="generatedSql" type="textarea" :rows="3" @input="onGeneratedSqlEdit" />
                <div class="sql-fix-actions">
                  <el-button size="mini" type="warning" :loading="executing" @click="executeGeneratedSql">执行修改后的 SQL</el-button>
                  <el-button size="mini" @click="switchToSqlMode(generatedSql)">跳转到 SQL 编辑模式</el-button>
                </div>
              </div>
            </transition>
            <div class="result-pane" :style="{ marginTop: '12px' }">
              <div class="result-toolbar" v-if="queryResult">
                <ExportButton
                  :db-name="activeDb"
                  :sql="generatedSql || ''"
                  :has-result="!!queryResult"
                  :show-prompt="showExportPrompt && queryMode === 'nl'"
                  @exported="onExported"
                  @dismiss-prompt="dismissExportPrompt"
                />
              </div>
              <ResultTable :result="queryResult" />
            </div>
          </div>
        </div>
      </template>
    </el-main>

    <!-- 添加连接对话框 -->
    <el-dialog title="添加数据库连接" :visible.sync="showAddDialog" width="480px" @close="resetAddForm" :close-on-click-modal="false">
      <el-form ref="addForm" :model="addForm" :rules="addRules" label-width="100px">
        <el-form-item label="连接名称" prop="dbName">
          <el-input v-model="addForm.dbName" placeholder="如：production-db" maxlength="128" show-word-limit />
        </el-form-item>
        <el-form-item label="JDBC URL" prop="dbUrl">
          <el-input v-model="addForm.dbUrl" type="textarea" :rows="3"
            placeholder="jdbc:postgresql://host:5432/db?user=user&password=pass" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="adding" @click="handleAdd">连接</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog title="确认删除" :visible.sync="showDeleteDialog" width="360px">
      <p style="color: #4e5969;">确认删除连接「<strong>{{ deleteTarget }}</strong>」？相关的 metadata 缓存也将一并清除。</p>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button type="danger" :loading="deleting" @click="handleDelete">删除</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script>
import { getDbs, addDb, getDbMetadata, queryDb, naturalQuery, extractErrorMessage } from '../services/api';
import SqlEditor from '../components/SqlEditor.vue';
import ResultTable from '../components/ResultTable.vue';
import ExportButton from '../components/ExportButton.vue';

export default {
  name: 'QueryPage',
  components: { SqlEditor, ResultTable, ExportButton },
  data() {
    return {
      dbs: [],
      loadingDbs: false,
      activeDb: '',
      metadata: [],
      loadingMetadata: false,
      refreshingMetadata: false,
      expandedTable: '',
      showAddDialog: false,
      adding: false,
      addForm: { dbName: '', dbUrl: '' },
      addRules: {
        dbName: [
          { required: true, message: '请输入连接名称', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9_-]+$/, message: '仅支持英文、数字、下划线和连字符', trigger: 'blur' },
        ],
        dbUrl: [
          { required: true, message: '请输入 JDBC URL', trigger: 'blur' },
          { pattern: /^jdbc:postgresql:\/\//, message: '必须以 jdbc:postgresql:// 开头', trigger: 'blur' },
        ],
      },
      queryMode: 'sql',
      currentSql: 'SELECT * FROM ',
      naturalText: '',
      generatedSql: '',
      executing: false,
      queryResult: null,
      showExportPrompt: false,
      showDeleteDialog: false,
      deleteTarget: '',
      deleting: false,
    };
  },
  computed: {
    expandedColumns() {
      const tbl = this.metadata.find(t => t.tableName === this.expandedTable);
      return tbl ? tbl.columns : [];
    },
  },
  created() {
    this.loadDbs();
  },
  methods: {
    async loadDbs() {
      this.loadingDbs = true;
      try {
        this.dbs = await getDbs();
        if (this.dbs.length > 0) {
          // 如果当前 activeDb 还在列表中则保留，否则选第一个
          const stillExists = this.dbs.some(d => d.dbName === this.activeDb);
          if (!stillExists) {
            this.activeDb = this.dbs[0].dbName;
            this.loadMetadata();
          }
        } else {
          this.activeDb = '';
          this.metadata = [];
          this.queryResult = null;
        }
      } catch (e) {
        const err = extractErrorMessage(e);
        this.$message.error('加载连接列表失败: ' + err.message);
      } finally {
        this.loadingDbs = false;
      }
    },
    async loadMetadata() {
      if (!this.activeDb) return;
      this.loadingMetadata = true;
      this.expandedTable = '';
      try {
        this.metadata = await getDbMetadata(this.activeDb);
      } catch (e) {
        const err = extractErrorMessage(e);
        this.$message.error('加载 metadata 失败: ' + err.message);
      } finally {
        this.loadingMetadata = false;
      }
    },
    onDbSelect(dbName) {
      if (dbName === this.activeDb) return;
      this.activeDb = dbName;
      this.queryResult = null;
      this.generatedSql = '';
      this.showExportPrompt = false;
      this.currentSql = 'SELECT * FROM ';
      this.loadMetadata();
    },
    async refreshMetadata() {
      if (!this.activeDb) return;
      this.refreshingMetadata = true;
      const old = this.metadata;
      try {
        this.metadata = await getDbMetadata(this.activeDb, true);
        this.$message.success('metadata 已更新');
      } catch (e) {
        this.metadata = old;
        const err = extractErrorMessage(e);
        this.$message.error(err.message + '（保留缓存）');
      } finally {
        this.refreshingMetadata = false;
      }
    },
    toggleTable(name) {
      this.expandedTable = this.expandedTable === name ? '' : name;
    },
    confirmDelete(dbName) {
      this.deleteTarget = dbName;
      this.showDeleteDialog = true;
    },
    async handleDelete() {
      if (!this.deleteTarget) return;
      this.deleting = true;
      try {
        // 调用后端删除 API — 直接用 fetch 调用 DELETE 方法
        const resp = await fetch(`/api/v1/dbs/${encodeURIComponent(this.deleteTarget)}`, { method: 'DELETE' });
        if (!resp.ok) {
          const data = await resp.json();
          throw new Error(data.detail?.message || '删除失败');
        }
        this.$message.success(`连接「${this.deleteTarget}」已删除`);
        this.showDeleteDialog = false;
        if (this.deleteTarget === this.activeDb) {
          this.activeDb = '';
          this.metadata = [];
          this.queryResult = null;
        }
        await this.loadDbs();
      } catch (e) {
        this.$message.error(e.message || '删除失败');
      } finally {
        this.deleting = false;
        this.deleteTarget = '';
      }
    },
    async handleAdd() {
      const valid = await this.$refs.addForm.validate().catch(() => false);
      if (!valid) return;
      this.adding = true;
      try {
        const result = await addDb(this.addForm.dbName, this.addForm.dbUrl);
        this.$message.success(`连接「${result.dbName}」添加成功`);
        this.showAddDialog = false;
        await this.loadDbs();
        this.activeDb = result.dbName;
        this.loadMetadata();
      } catch (e) {
        const err = extractErrorMessage(e);
        this.$message.error(err.message || '添加连接失败');
      } finally {
        this.adding = false;
      }
    },
    resetAddForm() {
      this.addForm = { dbName: '', dbUrl: '' };
      this.$refs.addForm?.clearValidate();
    },
    async handleQuery() {
      if (!this.currentSql.trim()) { this.$message.warning('请输入 SQL 语句'); return; }
      this.executing = true;
      this.queryResult = null;
      try {
        this.queryResult = await queryDb(this.activeDb, this.currentSql);
        this.showExportPrompt = true;
      } catch (e) {
        const err = extractErrorMessage(e);
        this.$message.error(err.message || '查询执行失败');
      } finally {
        this.executing = false;
      }
    },
    async handleNaturalQuery() {
      if (!this.naturalText.trim()) { this.$message.warning('请输入查询描述'); return; }
      this.executing = true;
      this.queryResult = null;
      this.generatedSql = '';
      try {
        this.queryResult = await naturalQuery(this.activeDb, this.naturalText);
        if (this.queryResult?.sqlExecuted) this.generatedSql = this.queryResult.sqlExecuted;
        this.showExportPrompt = true;
      } catch (e) {
        const d = e.response?.data?.detail;
        if (d?.generatedSql) this.generatedSql = d.generatedSql;
        const err = extractErrorMessage(e);
        this.$message.error(err.message || '自然语言查询失败');
      } finally {
        this.executing = false;
      }
    },
    onGeneratedSqlEdit(v) { this.generatedSql = v; },
    switchToSqlMode(sql) { this.queryMode = 'sql'; this.currentSql = sql; this.$message.success('已切换到 SQL 编辑模式'); },
    onExported() {
      this.showExportPrompt = false;
    },
    dismissExportPrompt() {
      this.showExportPrompt = false;
    },
    async executeGeneratedSql() {
      if (!this.generatedSql.trim()) return;
      this.executing = true;
      this.queryResult = null;
      try {
        this.queryResult = await queryDb(this.activeDb, this.generatedSql);
      } catch (e) {
        const err = extractErrorMessage(e);
        this.$message.error(err.message || '查询执行失败');
      } finally {
        this.executing = false;
      }
    },
  },
};
</script>

<style scoped>
/* ====== 侧边栏 ====== */
.sidebar {
  background: #ffffff;
  border-right: 1px solid #e5e6eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 16px 12px;
  border-bottom: 1px solid #f2f3f5;
}
.sidebar-title {
  font-weight: 600;
  font-size: 15px;
  color: #1d2129;
}
.token-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px 12px;
}
.sidebar-footer {
  padding: 10px 16px;
  border-top: 1px solid #f2f3f5;
  text-align: center;
}

/* ====== Token 风格 ====== */
.db-token {
  display: flex;
  align-items: stretch;
  padding: 10px 12px;
  margin-bottom: 6px;
  border-radius: 8px;
  border: 1px solid #e5e6eb;
  cursor: pointer;
  transition: all 0.15s ease;
  background: #ffffff;
}
.db-token:hover {
  border-color: #1677ff;
  box-shadow: 0 1px 4px rgba(22, 119, 255, 0.08);
}
.db-token-active {
  border-color: #1677ff;
  background: #f0f5ff;
  box-shadow: 0 1px 4px rgba(22, 119, 255, 0.12);
}
.token-indicator {
  width: 3px;
  background: transparent;
  border-radius: 2px;
  margin-right: 10px;
  flex-shrink: 0;
  transition: background 0.2s;
}
.db-token-active .token-indicator {
  background: #1677ff;
}
.token-content {
  flex: 1;
  min-width: 0;
}
.token-name {
  font-size: 13px;
  font-weight: 500;
  color: #1d2129;
  display: flex;
  align-items: center;
  margin-bottom: 2px;
}
.token-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.token-count {
  font-size: 11px;
  color: #86909c;
}
.token-delete {
  color: #c9cdd4;
  padding: 0;
  font-size: 14px;
}
.token-delete:hover {
  color: #f53f3f;
}

/* ====== 主内容 ====== */
.main-content {
  display: flex;
  flex-direction: column;
  padding: 0;
  background: #ffffff;
  overflow: hidden;
}

/* ====== 数据库信息栏 ====== */
.db-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f2f3f5;
  flex-shrink: 0;
}
.db-info-left {
  display: flex;
  align-items: center;
}
.db-info-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1d2129;
}
.db-info-right {
  display: flex;
  gap: 8px;
}

/* ====== Metadata 区 ====== */
.metadata-section {
  padding: 12px 20px;
  border-bottom: 1px solid #f2f3f5;
  flex-shrink: 0;
}
.section-label {
  font-size: 12px;
  font-weight: 500;
  color: #86909c;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.table-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.table-tab {
  display: inline-flex;
  align-items: center;
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid #e5e6eb;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
  background: #fafafa;
  gap: 3px;
}
.table-tab:hover {
  border-color: #1677ff;
  background: #f0f5ff;
}
.table-tab-active {
  border-color: #1677ff;
  background: #e6f4ff;
}

.columns-panel {
  margin-top: 8px;
  border: 1px solid #e5e6eb;
  border-radius: 6px;
  overflow: hidden;
}
.columns-header {
  padding: 6px 12px;
  font-size: 11px;
  font-weight: 500;
  color: #86909c;
  background: #fafafa;
  border-bottom: 1px solid #e5e6eb;
}
.columns-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.columns-table th {
  text-align: left;
  padding: 6px 12px;
  color: #4e5969;
  font-weight: 500;
  background: #fafafa;
  border-bottom: 1px solid #e5e6eb;
}
.columns-table td {
  padding: 5px 12px;
  border-bottom: 1px solid #f2f3f5;
  color: #4e5969;
}
.columns-table code {
  color: #1677ff;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}
.type-badge {
  background: #f2f3f5;
  padding: 1px 6px;
  border-radius: 3px;
  color: #4e5969;
  font-size: 11px;
}

/* ====== 查询区域 ====== */
.query-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.query-mode-bar {
  display: flex;
  align-items: center;
  padding: 8px 20px;
  border-bottom: 1px solid #e5e6eb;
  background: #fafafa;
  flex-shrink: 0;
}
.query-panel-split {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.editor-pane {
  height: 45%;
  min-height: 180px;
}
.result-pane {
  flex: 1;
  border-top: 1px solid #e5e6eb;
  overflow: auto;
  min-height: 120px;
}
.result-toolbar {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  border-bottom: 1px solid #e5e6eb;
  background: #fafafa;
  gap: 8px;
}
.query-panel-nl {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  min-height: 0;
  overflow-y: auto;
}
.nl-input-area {
  flex-shrink: 0;
}
.sql-fix-panel {
  border: 1px solid #ffd591;
  border-radius: 6px;
  padding: 12px;
  background: #fff7e6;
  margin-top: 12px;
}
.sql-fix-header {
  font-size: 12px;
  color: #ff7d00;
  margin-bottom: 8px;
}
.sql-fix-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
</style>
