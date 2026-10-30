const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path) {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) throw new Error(`API ${path}: ${response.status}`);
  return response.json();
}

export async function fetchHealth() {
  return request('/api/health');
}

export async function fetchSummary() {
  return request('/api/summary');
}

export async function fetchProvinces(params = {}) {
  const paramsString = new URLSearchParams(params).toString();
  return request(`/api/provinces${paramsString ? `?${paramsString}` : ''}`);
}

export async function fetchProvinceDetail(provinsiId) {
  return request(`/api/provinces/${encodeURIComponent(provinsiId)}`);
}

export async function fetchQuadrants() {
  return request('/api/quadrants');
}

export async function fetchGeoJSON() {
  return request('/api/geojson');
}

export async function simulatePolicy(payload) {
  const response = await fetch(`${API_BASE_URL}/api/simulate`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error(`API /api/simulate: ${response.status}`);
  return response.json();
}
