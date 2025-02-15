const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async get<T>(path: string): Promise<{ data: T }> {
    const response = await fetch(`${this.baseUrl}${path}`)
    const data = await response.json()
    return { data }
  }

  async post<T>(path: string, body?: unknown): Promise<{ data: T }> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    })
    const data = await response.json()
    return { data }
  }
}

export const api = new ApiClient(API_BASE_URL) 