async function readApiError(response, fallbackMessage) {
  let detail = fallbackMessage

  try {
    const body = await response.json()

    if (typeof body.detail === 'string') {
      detail = body.detail
    }
  } catch {
    // Keep fallback message.
  }

  if (response.status === 429) {
    return 'AI request limit reached. Please try again later.'
  }

  if (response.status === 503) {
    return 'AI service is temporarily unavailable. Please try again later.'
  }

  return detail
}

export async function analyzeSkills(payload) {
  const response = await fetch('/api/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const message = await readApiError(
      response,
      `Analysis failed (${response.status})`
    )

    throw new Error(message)
  }

  return response.json()
}

export async function extractDocument(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/documents/extract', {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const message = await readApiError(
      response,
      `Document extraction failed (${response.status})`
    )

    throw new Error(message)
  }

  return response.json()
}