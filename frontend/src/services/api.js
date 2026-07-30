const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api'

export class APIError extends Error {
  constructor(message, status = 500) {
    super(message)
    this.name = 'APIError'
    this.status = status
  }
}

async function request(endpoint, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        Accept: 'application/json',
        ...options.headers,
      },
      ...options,
    })
  } catch {
    throw new APIError(
      'Backend sunucusuna ulaşılamadı. FastAPI sunucusunun çalıştığını kontrol et.',
      0,
    )
  }

  let data

  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const message = data?.detail || `API isteği başarısız oldu. HTTP durum kodu: ${response.status}`

    throw new APIError(message, response.status)
  }

  return data
}

export function analyzeDeveloper(username) {
  return request(`/analysis/developers/${encodeURIComponent(username)}`, {
    method: 'POST',
  })
}

export function getDeveloperSkills(username) {
  return request(`/skills/developers/${encodeURIComponent(username)}`)
}

export function getGitHubPreview(username) {
  return request(`/github/users/${encodeURIComponent(username)}/preview`)
}

export function checkBackendHealth() {
  return request('/health')
}

export function getDeveloperRecommendations(username) {
  return request(`/recommendations/developers/${encodeURIComponent(username)}`)
}

export function getDeveloperGraph(username) {
  return request(`/graphs/developers/${encodeURIComponent(username)}`)
}

export function getSimilarDevelopers(username, limit = 5) {
  const query = new URLSearchParams({
    limit: String(limit),
  })

  return request(`/similarity/developers/${encodeURIComponent(username)}?${query}`)
}
