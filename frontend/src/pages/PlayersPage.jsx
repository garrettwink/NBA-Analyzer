import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export default function PlayersPage() {
  const [players, setPlayers] = useState([])
  
  useEffect(() => {
    fetch('http://localhost:8000/players')
      .then(response => response.json())
      .then(data => setPlayers(data))
      .catch(error => console.error('Error:', error))
  }, [])

  return (
    <div>
      <h1>NBA Players</h1>

      <ul>
        {players.map(player => (
          <li key={player.player_id}>
            <Link to={`/players/${player.player_id}`}>
              {player.name} - {player.position}
            </Link>
          </li>
        ))}
      </ul>
      
    </div>
  )
}