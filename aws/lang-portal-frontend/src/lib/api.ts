const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl
  }

  async get<T>(token: string, path: string): Promise<{ data: T }> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return { data }
  }

  async post<T>(token: string, path: string, body?: unknown): Promise<{ data: T }> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: body ? JSON.stringify(body) : undefined,
    })
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    return { data }
  }
}

export const api = new ApiClient(API_BASE_URL) 