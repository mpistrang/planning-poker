import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { SocketProvider } from './contexts/SocketContext'
import { RoomProvider } from './contexts/RoomContext'
import { Home } from './pages/Home'
import { Room } from './pages/Room'

function App() {
  return (
    <BrowserRouter>
      <SocketProvider>
        <RoomProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/room/:roomCode" element={<Room />} />
          </Routes>
        </RoomProvider>
      </SocketProvider>
    </BrowserRouter>
  )
}

export default App
