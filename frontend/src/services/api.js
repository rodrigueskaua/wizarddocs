const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, options)
  const isJson = response.headers.get('content-type')?.includes('application/json')
  const body = isJson ? await response.json() : null

  if (!response.ok) {
    throw new Error(body?.detail || `Erro ${response.status} ao chamar ${path}`)
  }
  return body
}

export function listDocuments() {
  return request('/documents/')
}

export function uploadPdf(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/upload-pdf/', { method: 'POST', body: formData })
}

export function deleteDocument(filename) {
  return request(`/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' })
}

export function listProviders() {
  return request('/providers/')
}

export function askQuestion({ question, provider, source, history }) {
  return request('/query/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, provider, source, history }),
  })
}
