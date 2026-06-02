const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    channel: 'msedge',
    timeout: 15000,
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 900 } });
  page.setDefaultTimeout(10000);

  // 打开页面
  await page.goto('http://localhost:8080', { waitUntil: 'load', timeout: 15000 });
  await page.waitForSelector('.sidebar', { timeout: 5000 });
  await page.waitForTimeout(500);

  // 点击连接
  const token = await page.$('.db-token');
  if (token) await token.click();
  await page.waitForTimeout(2000);

  // 等待编辑器加载
  await page.waitForSelector('.monaco-editor', { timeout: 5000 });
  await page.waitForTimeout(500);

  // 点击编辑器并粘贴文本
  const editorArea = await page.$('.monaco-editor');
  if (editorArea) {
    await editorArea.click();
    await page.waitForTimeout(300);
    // 用 clipboard 方式粘贴
    const sql = `SELECT category, COUNT(*) AS count, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
ORDER BY count DESC
LIMIT 1000;`;
    await page.evaluate((text) => {
      // Monaco editor侦听 input 事件 - 通过 textarea 原生 setter
      const ta = document.querySelector('.monaco-editor textarea');
      if (ta) {
        // 使用 execCommand 方式插入
        ta.focus();
        // 获取 Monaco 的当前 selection 并直接设置
        document.execCommand('insertText', false, text);
      }
    }, sql);
  }
  await page.waitForTimeout(1500);

  // 点击执行按钮
  const executeBtn = await page.$('button:has-text("执行")');
  if (executeBtn) {
    await executeBtn.click();
  }

  await page.waitForTimeout(3000);

  // 截图
  const screenshotPath = path.join(__dirname, 'query_result.png');
  await page.screenshot({ path: screenshotPath, fullPage: false });

  console.log('截图已保存:', screenshotPath);
  await browser.close();
})();
