import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Layout } from '../components/Layout'

export const Home: React.FC = () => {
  const [roomCode, setRoomCode] = useState('')
  const [userName, setUserName] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const navigate = useNavigate()

  const handleCreateRoom = () => {
    if (!userName.trim()) {
      alert('Please enter your name')
      return
    }
    setIsCreating(true)
    // Generate a random room code for new rooms
    const newRoomCode = Math.random().toString(36).substring(2, 8).toUpperCase()
    navigate(`/room/${newRoomCode}?name=${encodeURIComponent(userName)}`)
  }

  const handleJoinRoom = (e: React.FormEvent) => {
    e.preventDefault()
    if (!roomCode.trim()) {
      alert('Please enter a room code')
      return
    }
    if (!userName.trim()) {
      alert('Please enter your name')
      return
    }
    navigate(`/room/${roomCode.toUpperCase()}?name=${encodeURIComponent(userName)}`)
  }

  return (
    <Layout>
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            Welcome to Planning Poker
          </h2>

          <div className="mb-6">
            <label htmlFor="userName" className="block text-sm font-medium text-gray-700 mb-2">
              Your Name
            </label>
            <input
              type="text"
              id="userName"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your name"
            />
          </div>

          <div className="mb-6">
            <button
              onClick={handleCreateRoom}
              disabled={isCreating || !userName.trim()}
              className="w-full bg-blue-600 text-white px-6 py-3 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Create New Room
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">or</span>
            </div>
          </div>

          <form onSubmit={handleJoinRoom}>
            <div className="mb-4">
              <label htmlFor="roomCode" className="block text-sm font-medium text-gray-700 mb-2">
                Room Code
              </label>
              <input
                type="text"
                id="roomCode"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase"
                placeholder="ABCD12"
                maxLength={6}
              />
            </div>

            <button
              type="submit"
              disabled={!roomCode.trim() || !userName.trim()}
              className="w-full bg-green-600 text-white px-6 py-3 rounded-md font-medium hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              Join Room
            </button>
          </form>
        </div>
      </div>
    </Layout>
  )
}
