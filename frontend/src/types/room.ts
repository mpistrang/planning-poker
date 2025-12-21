import { User } from './user'

export interface VoteHistory {
  round: number
  votes: Record<string, string>
  revealed_at: string
}

export interface Room {
  room_code: string
  created_at: string
  state: 'voting' | 'revealed'
  current_round: number
  users: Record<string, User>
  vote_history: VoteHistory[]
}
