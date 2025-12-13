/**
 * Support Client
 * Client-facing helpers for fualt.txt + realendpoint.txt support endpoints.
 */

import { API_ENDPOINTS } from './config.js';

export class SupportClient {
  static async getFualt({ tail = 500 } = {}) {
    const url = `${API_ENDPOINTS.supportFualt}?tail=${encodeURIComponent(tail)}`;
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  }

  static async getRealEndpoints({ format = 'json' } = {}) {
    const url = `${API_ENDPOINTS.supportRealEndpoints}?format=${encodeURIComponent(format)}`;
    const res = await fetch(url, { headers: { 'Content-Type': 'application/json' } });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    if (format === 'txt') return await res.text();
    return await res.json();
  }
}

export default SupportClient;

