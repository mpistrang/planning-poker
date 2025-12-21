import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { useSocket } from './SocketContext'
import { Room } from '../types/room'
import { User } from '../types/user'
import {
  RoomJoinedData,
  UserJoinedData,
  UserLeftData,
  VoteSubmittedData,
  VotesRevealedData,
  RoundResetData,
  ErrorData,
  UserKickedData
} from '../types/events'

interface RoomContextType {
  room: Room | null
  currentUserId: string | null
  currentUser: User | null
  isFacilitator: boolean
  error: string | null
  joinRoom: (roomCode: string, userName: string) => void
  leaveRoom: () => void
  submitVote: (vote: string) => void
  clearVote: () => void
  revealVotes: () => void
  resetRound: () => void
  kickUser: (userId: string) => void
  clearError: () => void
}

const RoomContext = createContext<RoomContextType | null>(null)

export const useRoom = () => {
  const context = useContext(RoomContext)
  if (!context) {
    throw new Error('useRoom must be used within RoomProvider')
  }
  return context
}

interface RoomProviderProps {
  children: React.ReactNode
}

export const RoomProvider: React.FC<RoomProviderProps> = ({ children }) => {
  const { socket, connected } = useSocket()
  const [room, setRoom] = useState<Room | null>(null)
  const [currentUserId, setCurrentUserId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const currentUser = room && currentUserId ? room.users[currentUserId] : null
  const isFacilitator = currentUser?.is_facilitator || false

  // Socket event handlers
  useEffect(() => {
    if (!socket) return

    socket.on('room_joined', (data: RoomJoinedData) => {
      console.log('Joined room:', data)
      setCurrentUserId(data.user_id)
    })

    socket.on('room_state', (data: Room) => {
      console.log('Room state received:', data)
      console.log('Room state user IDs:', Object.keys(data.users))
      setRoom(data)
    })

    socket.on('user_joined', (data: UserJoinedData) => {
      console.log('User joined event received:', data)
      setRoom(prev => {
        if (!prev) {
          console.log('No previous room state, ignoring user_joined')
          return prev
        }
        // Don't add if user already exists (prevents duplicate when joining)
        if (prev.users[data.user.id]) {
          console.log('User already exists, skipping:', data.user.id)
          return prev
        }
        console.log('Adding new user:', data.user.id)
        return {
          ...prev,
          users: {
            ...prev.users,
            [data.user.id]: data.user
          }
        }
      })
    })

    socket.on('user_left', (data: UserLeftData) => {
      console.log('User left:', data)
      setRoom(prev => {
        if (!prev) return prev
        const { [data.user_id]: removed, ...remainingUsers } = prev.users
        return {
          ...prev,
          users: remainingUsers
        }
      })
    })

    socket.on('user_disconnected', (data: { user_id: string }) => {
      console.log('User disconnected:', data)
      setRoom(prev => {
        if (!prev || !prev.users[data.user_id]) return prev
        return {
          ...prev,
          users: {
            ...prev.users,
            [data.user_id]: {
              ...prev.users[data.user_id],
              connected: false
            }
          }
        }
      })
    })

    socket.on('vote_submitted', (data: VoteSubmittedData) => {
      console.log('Vote submitted:', data)
      // Update UI to show user has voted (without revealing value)
      // For other users, show 'hidden' placeholder. For current user, keep their actual vote
      setRoom(prev => {
        if (!prev || !prev.users[data.user_id]) return prev

        // Don't override the current user's vote - they can see their own vote
        if (data.user_id === currentUserId) {
          return prev
        }

        return {
          ...prev,
          users: {
            ...prev.users,
            [data.user_id]: {
              ...prev.users[data.user_id],
              current_vote: 'hidden' // Placeholder to show they voted
            }
          }
        }
      })
    })

    socket.on('vote_cleared', (data: { user_id: string }) => {
      setRoom(prev => {
        if (!prev || !prev.users[data.user_id]) return prev
        return {
          ...prev,
          users: {
            ...prev.users,
            [data.user_id]: {
              ...prev.users[data.user_id],
              current_vote: null
            }
          }
        }
      })
    })

    socket.on('votes_revealed', (data: VotesRevealedData) => {
      console.log('Votes revealed:', data)
      setRoom(prev => {
        if (!prev) return prev
        const updatedUsers = { ...prev.users }
        Object.entries(data.votes).forEach(([userId, vote]) => {
          if (updatedUsers[userId]) {
            updatedUsers[userId] = {
              ...updatedUsers[userId],
              current_vote: vote
            }
          }
        })
        return {
          ...prev,
          state: 'revealed',
          users: updatedUsers
        }
      })
    })

    socket.on('round_reset', (data: RoundResetData) => {
      console.log('Round reset:', data)
      setRoom(prev => {
        if (!prev) return prev
        const clearedUsers = Object.fromEntries(
          Object.entries(prev.users).map(([id, user]) => [
            id,
            { ...user, current_vote: null }
          ])
        )
        return {
          ...prev,
          state: 'voting',
          current_round: data.round,
          users: clearedUsers
        }
      })
    })

    socket.on('user_kicked', (data: UserKickedData) => {
      console.log('User kicked:', data)
      // If it's me being kicked, show message and clear room
      if (data.user_id === currentUserId) {
        setError('You have been removed from the room by the facilitator')
        setRoom(null)
        setCurrentUserId(null)
      }
    })

    socket.on('error', (data: ErrorData) => {
      console.error('Socket error:', data)
      setError(data.message)
    })

    return () => {
      socket.off('room_joined')
      socket.off('room_state')
      socket.off('user_joined')
      socket.off('user_left')
      socket.off('user_disconnected')
      socket.off('vote_submitted')
      socket.off('vote_cleared')
      socket.off('votes_revealed')
      socket.off('round_reset')
      socket.off('user_kicked')
      socket.off('error')
    }
  }, [socket, currentUserId])

  const joinRoom = useCallback((roomCode: string, userName: string) => {
    if (!socket || !connected) {
      setError('Not connected to server')
      return
    }
    socket.emit('join_room', { room_code: roomCode, user_name: userName })
  }, [socket, connected])

  const leaveRoom = useCallback(() => {
    if (!socket) return
    socket.emit('leave_room')
    setRoom(null)
    setCurrentUserId(null)
  }, [socket])

  const submitVote = useCallback((vote: string) => {
    if (!socket || !currentUserId) return

    // Optimistically update local state so user sees their vote immediately
    setRoom(prev => {
      if (!prev || !prev.users[currentUserId]) return prev
      return {
        ...prev,
        users: {
          ...prev.users,
          [currentUserId]: {
            ...prev.users[currentUserId],
            current_vote: vote
          }
        }
      }
    })

    socket.emit('submit_vote', { vote })
  }, [socket, currentUserId])

  const clearVote = useCallback(() => {
    if (!socket) return
    socket.emit('clear_vote')
  }, [socket])

  const revealVotes = useCallback(() => {
    if (!socket) return
    socket.emit('reveal_votes')
  }, [socket])

  const resetRound = useCallback(() => {
    if (!socket) return
    socket.emit('reset_round')
  }, [socket])

  const kickUser = useCallback((userId: string) => {
    if (!socket) return
    socket.emit('kick_user', { user_id: userId })
  }, [socket])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return (
    <RoomContext.Provider
      value={{
        room,
        currentUserId,
        currentUser,
        isFacilitator,
        error,
        joinRoom,
        leaveRoom,
        submitVote,
        clearVote,
        revealVotes,
        resetRound,
        kickUser,
        clearError
      }}
    >
      {children}
    </RoomContext.Provider>
  )
}
