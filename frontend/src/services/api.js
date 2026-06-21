import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60000, // 60s 超时（后端 metadata 获取上限 30s + 余量）
});

// 统一错误提取：将网络/超时错误转成与后端一致的结构
export function extractErrorMessage(error) {
  if (error.code === 'ECONNABORTED') {
    return { code: 'TIMEOUT', message: '连接超时，请检查网络或数据库地址' };
  }
  if (!error.response) {
    return { code: 'NETWORK_ERROR', message: '无法连接到后端服务，请确认后端已启动' };
  }
  const detail = error.response.data?.detail;
  if (detail) {
    return { code: detail.code || 'UNKNOWN', message: detail.message || '未知错误' };
  }
  return { code: 'UNKNOWN', message: error.message || '请求失败' };
}

export function getDbs() {
  return api.get('/dbs').then(r => r.data);
}

export function addDb(dbName, dbUrl) {
  return api.post(`/dbs/${encodeURIComponent(dbName)}`, { db_url: dbUrl }).then(r => r.data);
}

export function getDbMetadata(dbName, refresh = false) {
  return api.get(`/dbs/${encodeURIComponent(dbName)}`, { params: { refresh } }).then(r => r.data);
}

export function queryDb(dbName, sql) {
  return api.post(`/dbs/${encodeURIComponent(dbName)}/query`, { sql }).then(r => r.data);
}

export function naturalQuery(dbName, natural) {
  return api.post(`/dbs/${encodeURIComponent(dbName)}/query/natural`, { natural }).then(r => r.data);
}

/**
 * 导出查询结果为文件。
 * 将结果作为 Blob 下载，而非解析 JSON。
 */
export function exportQuery(dbName, sql, format) {
  return api.post(
    `/dbs/${encodeURIComponent(dbName)}/query?export=${encodeURIComponent(format)}`,
    { sql },
    { responseType: 'blob' },
  ).then(r => ({
    blob: r.data,
    filename: extractFilenameFromHeaders(r.headers),
  }));
}

function extractFilenameFromHeaders(headers) {
  const disposition = headers['content-disposition'];
  if (disposition) {
    const match = disposition.match(/filename="?(.+?)"?$/);
    if (match) return match[1];
  }
  return 'export.csv';
}

export default api;
