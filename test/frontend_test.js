const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true, channel: 'msedge' });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();

  const results = [];

  async function test(name, fn) {
    try {
      await fn();
      results.push(`| ${name} | ✅ 通过 |`);
    } catch (e) {
      results.push(`| ${name} | ❌ 失败: ${e.message} |`);
    }
  }

  // TC-UI-001: 首次加载
  await test('TC-UI-001 首次加载空状态', async () => {
    await page.goto('http://localhost:8080', { waitUntil: 'networkidle' });
    const body = await page.textContent('body');
    if (!body.includes('暂无连接')) throw new Error('未显示空状态提示');
    if (!body.includes('请从左侧选择一个数据库连接')) throw new Error('未显示引导提示');
  });

  // TC-UI-002: 打开添加对话框
  await test('TC-UI-002 打开添加对话框', async () => {
    await page.click('text=添加');
    await page.waitForSelector('.el-dialog', { timeout: 3000 });
    const dialogText = await page.textContent('.el-dialog');
    if (!dialogText.includes('添加数据库连接')) throw new Error('对话框标题错误');
    if (!dialogText.includes('连接名称')) throw new Error('缺少连接名称字段');
    if (!dialogText.includes('JDBC URL')) throw new Error('缺少 JDBC URL 字段');
  });

  // TC-UI-003: 表单验证
  await test('TC-UI-003 表单验证空字段', async () => {
    await page.click('.el-dialog .el-button--primary');
    await page.waitForTimeout(500);
    const errors = await page.textContent('.el-dialog');
    if (!errors.includes('请输入连接名称')) throw new Error('未显示连接名称错误');
  });

  // TC-UI-004: JDBC URL 格式验证
  await test('TC-UI-004 JDBC URL 格式验证', async () => {
    await page.fill('.el-dialog input', 'testui');
    const textareas = await page.$$('.el-dialog textarea');
    await textareas[0].fill('mysql://localhost:3306/test');
    await page.click('.el-dialog .el-button--primary');
    await page.waitForTimeout(500);
    const errors = await page.textContent('.el-dialog');
    if (!errors.includes('jdbc:postgresql')) throw new Error('未显示 JDBC URL 格式错误');
  });

  // TC-UI-005: 添加连接成功
  await test('TC-UI-005 添加连接成功', async () => {
    // Close dialog first
    await page.click('.el-dialog .el-button--default');
    await page.waitForTimeout(300);
    await page.click('text=添加');
    await page.waitForSelector('.el-dialog', { timeout: 3000 });
    await page.waitForTimeout(300);
    // Fill form
    await page.fill('.el-dialog input', 'testui');
    const textareas = await page.$$('.el-dialog textarea');
    await textareas[0].fill('jdbc:postgresql://localhost:5432/testdb?user=postgres&password=postgres');
    await page.click('.el-dialog .el-button--primary');
    await page.waitForTimeout(3000);
    const body = await page.textContent('body');
    if (!body.includes('testui')) throw new Error('连接未显示在列表');
    results.push(`| TC-UI-005 添加连接成功 | ✅ 通过 |`);
    return;
  });

  // TC-UI-008: 树形结构
  await test('TC-UI-008 树形结构展示', async () => {
    await page.click('text=testdb');
    await page.waitForTimeout(2000);
    const body = await page.textContent('body');
    if (!body.includes('users') || !body.includes('products')) throw new Error('未显示表/视图树');
  });

  // TC-UI-009: 展开列信息
  await test('TC-UI-009 展开查看列信息', async () => {
    const expandBtns = await page.$$('.el-tree-node__expand-icon');
    if (expandBtns.length > 0) {
      await expandBtns[0].click();
      await page.waitForTimeout(500);
    }
    const body = await page.textContent('body');
    if (!body.includes('integer')) throw new Error('未显示列数据类型');
  });

  // TC-UI-012: Monaco Editor 渲染
  await test('TC-UI-012 Monaco Editor 渲染', async () => {
    const body = await page.textContent('body');
    if (!body.includes('Ctrl+Enter')) throw new Error('未显示 SQL 编辑器工具栏');
    if (!body.includes('执行')) throw new Error('未显示执行按钮');
  });

  // TC-UI-013: SQL 查询执行
  await test('TC-UI-013 SQL 查询执行', async () => {
    // Click SQL mode and type query
    await page.click('text=SQL 编辑');
    await page.waitForTimeout(300);
    const editor = await page.$('.monaco-editor');
    if (editor) {
      await editor.click();
      await page.keyboard.selectAll();
      await page.keyboard.type('SELECT * FROM users');
    }
    await page.click('button:has-text("执行")');
    await page.waitForTimeout(3000);
    const body = await page.textContent('body');
    if (!body.includes('Alice Wang')) throw new Error('查询结果未显示');
    if (!body.includes('5 行')) throw new Error('行数未显示');
  });

  // TC-UI-016: 非 SELECT 拒绝
  await test('TC-UI-016 非 SELECT 拒绝', async () => {
    const editor = await page.$('.monaco-editor');
    if (editor) {
      await editor.click();
      await page.keyboard.selectAll();
      await page.keyboard.type('DELETE FROM users');
    }
    await page.click('button:has-text("执行")');
    await page.waitForTimeout(2000);
    const body = await page.textContent('body');
    if (!body.includes('仅支持 SELECT')) throw new Error('未拒绝非 SELECT 语句');
  });

  // TC-UI-021: 模式切换
  await test('TC-UI-021 自然语言模式切换', async () => {
    await page.click('text=自然语言');
    await page.waitForTimeout(500);
    const body = await page.textContent('body');
    if (!body.includes('生成 SQL 并查询')) throw new Error('未显示自然语言模式');
  });

  // TC-UI-024: 刷新 metadata
  await test('TC-UI-024 刷新 metadata', async () => {
    await page.click('text=SQL 编辑');
    await page.waitForTimeout(300);
    const refreshBtn = await page.$('button:has-text("刷新")');
    if (refreshBtn) {
      await refreshBtn.click();
      await page.waitForTimeout(3000);
    }
    const body = await page.textContent('body');
    if (!body.includes('users')) throw new Error('刷新后表树未显示');
  });

  // TC-UI-007: 切换连接
  await test('TC-UI-007 切换数据库连接', async () => {
    await page.click('text=testdb');
    await page.waitForTimeout(1000);
    const body = await page.textContent('body');
    if (!body.includes('orders')) throw new Error('切换连接后未显示新表');
  });

  console.log('\n## 前端测试结果\n');
  console.log('| 用例 | 结果 |');
  console.log('|------|------|');
  results.forEach(r => console.log(r));

  await browser.close();
})();
