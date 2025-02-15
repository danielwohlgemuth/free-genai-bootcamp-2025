export interface Pagination {
  current_page: number
  total_pages: number
  total_items: number
  items_per_page: number
}

export interface PaginatedResponse<T> {
  items: T[]
  pagination: Pagination
}

export interface StudySession {
  id: number
  activity_name: string
  group_name: string
  start_time: string
  end_time: string
  review_items_count: number
}

export interface Word {
  id: string
  japanese: string
  romaji: string
  english: string
  correct_count: number
  wrong_count: number
}

export interface Group {
  id: number
  name: string
  word_count: number
}

export interface DashboardStats {
  success_rate: number
  total_study_sessions: number
  total_active_groups: number
  study_streak_days: number
} 