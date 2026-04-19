const API_URL = import.meta.env.VITE_API_URL?.trim() || ''

async function request(path, options = {}) {
  if (!API_URL) {
    throw new Error('VITE_API_URL is not configured for this build. Set it to your deployed backend URL in Vercel.')
  }

  let response

  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: {
        ...(options.headers || {}),
      },
      ...options,
    })
  } catch (error) {
    throw new Error(`Unable to reach backend at ${API_URL}. Check VITE_API_URL and CORS settings.`)
  }

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
