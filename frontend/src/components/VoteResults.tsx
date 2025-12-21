import React from 'react'
import { useRoom } from '../contexts/RoomContext'

export const VoteResults: React.FC = () => {
  const { room } = useRoom()

  if (!room || room.state !== 'revealed') return null

  const votes = Object.entries(room.users)
    .filter(([_, user]) => user.current_vote)
    .map(([_userId, user]) => ({
      name: user.name,
      vote: user.current_vote!
    }))

  // Calculate average (excluding ? and ☕)
  const numericVotes = votes
    .map(v => v.vote)
    .filter(v => !['?', '☕'].includes(v))
    .map(v => parseFloat(v))

  const average = numericVotes.length > 0
    ? (numericVotes.reduce((a, b) => a + b, 0) / numericVotes.length).toFixed(1)
    : 'N/A'

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Results</h3>

      <div className="mb-6">
        <div className="text-center">
          <div className="text-sm text-gray-600 mb-1">Average</div>
          <div className="text-4xl font-bold text-blue-600">{average}</div>
        </div>
      </div>

      <div className="space-y-2">
        {votes.map((vote, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
            <span className="font-medium text-gray-900">{vote.name}</span>
            <span className="text-2xl font-bold text-blue-600">{vote.vote}</span>
          </div>
        ))}
      </div>

      {votes.length === 0 && (
        <p className="text-center text-gray-500">No votes submitted</p>
      )}
    </div>
  )
}
