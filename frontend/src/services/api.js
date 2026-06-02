import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

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

export default api;
