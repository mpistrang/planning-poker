import React from 'react'
import { useRoom } from '../contexts/RoomContext'

export const VotingStatus: React.FC = () => {
  const { room, currentUserId, isFacilitator, kickUser } = useRoom()

  if (!room) return null

  const users = Object.values(room.users)

  const handleKickUser = (userId: string, userName: string) => {
    if (window.confirm(`Are you sure you want to remove ${userName} from the room?`)) {
      kickUser(userId)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Participants</h3>
      <div className="space-y-2">
        {users.map((user) => (
          <div
            key={user.id}
            className={`flex items-center justify-between p-3 rounded-md ${
              user.id === currentUserId ? 'bg-blue-50' : 'bg-gray-50'
            }`}
          >
            <div className="flex items-center space-x-3">
              <div
                className={`h-3 w-3 rounded-full ${
                  user.connected ? 'bg-green-500' : 'bg-gray-400'
                }`}
              />
              <span className="font-medium text-gray-900">
                {user.name}
                {user.id === currentUserId && ' (You)'}
              </span>
              {user.is_facilitator && (
                <span className="px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded">
                  Facilitator
                </span>
              )}
            </div>
            <div className="flex items-center space-x-2">
              {user.current_vote && (
                <span className="text-green-600 font-bold">✓</span>
              )}
              {isFacilitator && user.id !== currentUserId && (
                <button
                  onClick={() => handleKickUser(user.id, user.name)}
                  className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                  title={`Remove ${user.name}`}
                >
                  Remove
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
