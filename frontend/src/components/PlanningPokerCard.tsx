import React from 'react'

interface PlanningPokerCardProps {
  value: string
  selected?: boolean
  onClick?: () => void
  disabled?: boolean
}

export const PlanningPokerCard: React.FC<PlanningPokerCardProps> = ({
  value,
  selected = false,
  onClick,
  disabled = false
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        aspect-[2/3] p-4 rounded-lg border-2 font-bold text-2xl
        transition-all duration-200 transform
        ${selected
          ? 'bg-blue-600 text-white border-blue-600 scale-105 shadow-lg'
          : 'bg-white text-gray-800 border-gray-300 hover:border-blue-400 hover:shadow-md'
        }
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-105'}
      `}
    >
      {value}
    </button>
  )
}
