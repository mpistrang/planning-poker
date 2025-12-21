import React from 'react'
import { PlanningPokerCard } from './PlanningPokerCard'
import { CARD_VALUES } from '../utils/constants'
import { useRoom } from '../contexts/RoomContext'

export const CardSelector: React.FC = () => {
  const { room, currentUser, submitVote } = useRoom()

  const myVote = currentUser?.current_vote

  const handleCardClick = (value: string) => {
    submitVote(value)
  }

  const isRevealed = room?.state === 'revealed'

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Select Your Estimate</h3>
      <div className="grid grid-cols-5 gap-4">
        {CARD_VALUES.map((value) => (
          <PlanningPokerCard
            key={value}
            value={value}
            selected={myVote === value}
            onClick={() => handleCardClick(value)}
            disabled={isRevealed}
          />
        ))}
      </div>
      {myVote && myVote !== 'hidden' && (
        <p className="mt-4 text-center text-sm text-gray-600">
          Your vote: <span className="font-bold">{myVote}</span>
        </p>
      )}
    </div>
  )
}
