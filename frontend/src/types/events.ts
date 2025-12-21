import { User } from './user'
import { Room } from './room'

export interface JoinRoomData {
  room_code: string
  user_name: string
}

export interface SubmitVoteData {
  vote: string
}

export interface RoomJoinedData {
  room_code: string
  user_id: string
  is_facilitator: boolean
}

export interface UserJoinedData {
  user: User
}

export interface UserLeftData {
  user_id: string
}

export interface UserDisconnectedData {
  user_id: string
}

export interface VoteSubmittedData {
  user_id: string
}

export interface VoteClearedData {
  user_id: string
}

export interface VotesRevealedData {
  votes: Record<string, string>
}

export interface RoundResetData {
  round: number
}

export interface ErrorData {
  message: string
  code?: string
}

export interface KickUserData {
  user_id: string
}

export interface UserKickedData {
  user_id: string
  kicked_by: string
}
