export interface User {
  id: string
  name: string
  connected: boolean
  is_facilitator: boolean
  current_vote: string | null
  joined_at: string
}
