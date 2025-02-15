const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

interface ApiResponse<T> {
  data?: T;
  error?: string
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return { data }
  } catch (error) {
    return { error: error instanceof Error ? error.message : 'Unknown error occurred' }
  }
}

export const api = {
  async get<T>(path: string): Promise<ApiResponse<T>> {
    return fetchApi<T>(path)
  },
  async post<T>(path: string, body?: unknown): Promise<ApiResponse<T>> {
    return fetchApi<T>(path, {
      method: 'POST',
      body: JSON.stringify(body),
    })
  },
} 