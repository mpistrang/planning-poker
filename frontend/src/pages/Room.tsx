import React, { useEffect, useState, useRef } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { CardSelector } from '../components/CardSelector'
import { VotingStatus } from '../components/VotingStatus'
import { VoteResults } from '../components/VoteResults'
import { RoomControls } from '../components/RoomControls'
import { useRoom } from '../contexts/RoomContext'
import { useSocket } from '../contexts/SocketContext'

export const Room: React.FC = () => {
  const { roomCode } = useParams<{ roomCode: string }>()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { connected } = useSocket()
  const { room, joinRoom, leaveRoom, error, clearError } = useRoom()
  const [hasJoined, setHasJoined] = useState(false)
  const joinAttemptedRef = useRef(false)
  const leaveRoomRef = useRef(leaveRoom)

  const userName = searchParams.get('name')

  // Keep leaveRoom ref updated
  useEffect(() => {
    leaveRoomRef.current = leaveRoom
  }, [leaveRoom])

  useEffect(() => {
    if (!roomCode || !userName) {
      navigate('/')
      return
    }

    if (connected && !hasJoined && !joinAttemptedRef.current) {
      joinAttemptedRef.current = true
      joinRoom(roomCode, userName)
      setHasJoined(true)
    }
  }, [roomCode, userName, connected, hasJoined, joinRoom, navigate])

  // Cleanup effect - only runs on unmount
  useEffect(() => {
    return () => {
      if (joinAttemptedRef.current) {
        leaveRoomRef.current()
      }
    }
  }, [])

  const handleCopyRoomCode = () => {
    if (room) {
      navigator.clipboard.writeText(room.room_code)
      alert('Room code copied to clipboard!')
    }
  }

  const handleLeaveRoom = () => {
    leaveRoom()
    navigate('/')
  }

  if (!connected) {
    return (
      <Layout>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Connecting to server...</p>
        </div>
      </Layout>
    )
  }

  if (!room) {
    return (
      <Layout>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Joining room...</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
          <button
            onClick={clearError}
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
          >
            <span className="text-xl">&times;</span>
          </button>
        </div>
      )}

      <div className="mb-6">
        <div className="bg-white rounded-lg shadow-md p-4 flex justify-between items-center">
          <div>
            <h2 className="text-sm text-gray-600">Room Code</h2>
            <p className="text-2xl font-bold text-gray-900">{room.room_code}</p>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={handleCopyRoomCode}
              className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
            >
              Copy Code
            </button>
            <button
              onClick={handleLeaveRoom}
              className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors"
            >
              Leave Room
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <CardSelector />
          {room.state === 'revealed' && <VoteResults />}
        </div>

        <div className="space-y-6">
          <VotingStatus />
          <RoomControls />
        </div>
      </div>
    </Layout>
  )
}
