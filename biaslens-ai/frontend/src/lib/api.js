const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    const errorPayload = await response.json().catch(() => ({}))
    throw new Error(errorPayload.detail || `Request failed: ${response.status}`)
  }

  return response.json()
}

export async function uploadArtifacts(file, modelFile, targetColumn) {
  const formData = new FormData()
  formData.append('file', file)
  if (modelFile) {
    formData.append('model_file', modelFile)
  }
  if (targetColumn) {
    formData.append('target_column', targetColumn)
  }

  return request('/upload', {
    method: 'POST',
    body: formData,
  })
}

export async function analyzeBias(payload) {
  return request('/analyze-bias', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
}

export async function mitigateBias(payload) {
  return request('/mitigate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
}

export async function explainBias(payload) {
  return request('/explain', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
}
