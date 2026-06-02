const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    channel: 'msedge',
    timeout: 15000,
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 900 } });

  // 打开前端页面
  await page.goto('http://localhost:8080', { waitUntil: 'load', timeout: 15000 });
  await page.waitForSelector('.sidebar', { timeout: 5000 });
  await page.waitForTimeout(500);

  // 点击已存在的连接（第一个 token）
  const activeToken = await page.$('.db-token');
  if (activeToken) {
    await activeToken.click();
    await page.waitForTimeout(2000);
  }

  // 先通过 API 执行查询，确保有结果
  await page.evaluate(async () => {
    const resp = await fetch('/api/v1/dbs/PostgreSQL/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sql: `SELECT category, COUNT(*) AS count, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
ORDER BY count DESC
LIMIT 1000;`
      }),
    });
    const data = await resp.json();
    // Store result reference on window for later
    window.__queryResult = data;
  });

  // 刷新页面让查询结果通过 UI 展示
  await page.reload({ waitUntil: 'load', timeout: 15000 });
  await page.waitForSelector('.sidebar', { timeout: 5000 });
  await page.waitForTimeout(1000);

  // 点击连接 token
  const token = await page.$('.db-token');
  if (token) await token.click();
  await page.waitForTimeout(1500);

  // 模拟输入 SQL：点击编辑器区域然后通过剪切板粘贴
  const editorArea = await page.$('.monaco-editor');
  if (editorArea) {
    await editorArea.click();
    await page.waitForTimeout(300);
    // Select all and delete
    await page.keyboard.press('Control+a');
    await page.waitForTimeout(100);
    await page.keyboard.press('Delete');
    await page.waitForTimeout(100);
    // Type the SQL
    await page.keyboard.type(`SELECT category, COUNT(*) AS count, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
ORDER BY count DESC
LIMIT 1000;`, { delay: 15 });
    await page.waitForTimeout(500);
  }

  // 点击「执行」按钮
  const executeBtn = await page.$('button:has-text("执行")');
  if (executeBtn) {
    await executeBtn.click();
  }

  // 等待查询结果显示
  await page.waitForTimeout(3000);

  // 截取全屏
  await page.screenshot({
    path: path.join(__dirname, 'query_result.png'),
    fullPage: false,
  });

  console.log('截图已保存到 test/query_result.png');

  await browser.close();
})();
