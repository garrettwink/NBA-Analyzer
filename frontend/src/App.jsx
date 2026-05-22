import {useEffect, useState } from 'react'
import './App.css'

function App() {
  const [players, setPlayers] = useState([])
  
  useEffect(() => {
    fetch('http://localhost:8000/players')
      .then(response => response.json())
      .then(data => {
        setPlayers(data)
      })
      .catch(error => console.error('Error fetching players:', error))
  })


  return (
    <>
      <div>
        <h1>NBA Players</h1>
        <ul>
          {players.map(player => (
            <li key={player.id}>
              {player.name} - {player.position}
            </li>
          ))}
        </ul>
      </div>
    </>
  )
}

export default App
