import React from 'react'
import { useRoom } from '../contexts/RoomContext'

export const RoomControls: React.FC = () => {
  const { room, isFacilitator, revealVotes, resetRound } = useRoom()

  if (!room || !isFacilitator) return null

  const hasVotes = Object.values(room.users).some(user => user.current_vote)
  const isRevealed = room.state === 'revealed'

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Facilitator Controls
      </h3>

      <div className="flex flex-col space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Round:</span>
          <span className="font-bold text-gray-900">{room.current_round}</span>
        </div>

        {!isRevealed ? (
          <button
            onClick={revealVotes}
            disabled={!hasVotes}
            className="w-full bg-green-600 text-white px-4 py-2 rounded-md font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Reveal Votes
          </button>
        ) : (
          <button
            onClick={resetRound}
            className="w-full bg-blue-600 text-white px-4 py-2 rounded-md font-medium hover:bg-blue-700 transition-colors"
          >
            Start New Round
          </button>
        )}
      </div>
    </div>
  )
}
